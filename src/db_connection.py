"""
数据库连接模块
提供MySQL数据库连接功能
支持自动重连和连接健康检查
"""

import pymysql
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """数据库连接管理类"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 3306,
                 user: str = "edge-llm",
                 password: str = "edge-llm",
                 database: str = "edge-llm",
                 charset: str = "utf8mb4",
                 connect_timeout: int = 10,
                 read_timeout: int = 30,
                 write_timeout: int = 30,
                 max_retries: int = 3):
        """
        初始化数据库连接参数
        
        Args:
            host: 数据库主机地址
            port: 数据库端口
            user: 用户名
            password: 密码
            database: 数据库名
            charset: 字符集
            connect_timeout: 连接超时时间（秒）
            read_timeout: 读取超时时间（秒）
            write_timeout: 写入超时时间（秒）
            max_retries: 最大重试次数
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.max_retries = max_retries
        self.connection: Optional[pymysql.Connection] = None
        self.last_used_time = 0
    
    def connect(self) -> pymysql.Connection:
        """
        建立数据库连接
        
        Returns:
            数据库连接对象
        """
        # 关闭旧连接
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                connect_timeout=self.connect_timeout,
                read_timeout=self.read_timeout,
                write_timeout=self.write_timeout
            )
            self.last_used_time = time.time()
            logger.info(f"成功连接到数据库 {self.database}")
            return self.connection
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            self.connection = None
            raise
    
    def _is_connection_alive(self) -> bool:
        """
        检查连接是否有效
        
        Returns:
            连接是否有效
        """
        if self.connection is None:
            return False
        
        try:
            # 使用ping检查连接
            self.connection.ping(reconnect=False)
            return True
        except:
            return False
    
    def _ensure_connection(self):
        """
        确保连接有效，如果无效则重连
        """
        if not self._is_connection_alive():
            logger.warning("数据库连接已断开，正在重新连接...")
            self.connect()
    
    def get_connection(self) -> pymysql.Connection:
        """
        获取数据库连接（如果未连接或连接无效则自动连接）
        
        Returns:
            数据库连接对象
        """
        if self.connection is None or not self.connection.open:
            return self.connect()
        
        # 检查连接是否有效
        self._ensure_connection()
        self.last_used_time = time.time()
        return self.connection
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        执行查询语句（带自动重连）
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        for attempt in range(self.max_retries):
            try:
                conn = self.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchall()
                    self.last_used_time = time.time()
                    return result
            except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
                error_code = e.args[0] if e.args else 0
                # 2006: MySQL server has gone away
                # 2013: Lost connection to MySQL server
                if error_code in (2006, 2013) and attempt < self.max_retries - 1:
                    logger.warning(f"数据库连接错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                    # 关闭旧连接并重连
                    self.connection = None
                    time.sleep(0.5)  # 短暂等待后重试
                    continue
                else:
                    logger.error(f"查询执行失败: {e}")
                    raise
            except Exception as e:
                logger.error(f"查询执行失败: {e}")
                raise
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）（带自动重连）
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            受影响的行数
        """
        conn = None
        for attempt in range(self.max_retries):
            try:
                conn = self.get_connection()
                with conn.cursor() as cursor:
                    affected_rows = cursor.execute(query, params)
                    conn.commit()
                    self.last_used_time = time.time()
                    return affected_rows
            except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
                error_code = e.args[0] if e.args else 0
                if error_code in (2006, 2013) and attempt < self.max_retries - 1:
                    logger.warning(f"数据库连接错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                    self.connection = None
                    conn = None
                    time.sleep(0.5)
                    continue
                else:
                    logger.error(f"更新执行失败: {e}")
                    if conn:
                        try:
                            conn.rollback()
                        except:
                            pass
                    raise
            except Exception as e:
                logger.error(f"更新执行失败: {e}")
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                raise
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        批量执行更新语句（带自动重连）
        
        Args:
            query: SQL更新语句
            params_list: 参数列表
            
        Returns:
            受影响的行数
        """
        conn = None
        for attempt in range(self.max_retries):
            try:
                conn = self.get_connection()
                with conn.cursor() as cursor:
                    affected_rows = cursor.executemany(query, params_list)
                    conn.commit()
                    self.last_used_time = time.time()
                    return affected_rows
            except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
                error_code = e.args[0] if e.args else 0
                if error_code in (2006, 2013) and attempt < self.max_retries - 1:
                    logger.warning(f"数据库连接错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                    self.connection = None
                    conn = None
                    time.sleep(0.5)
                    continue
                else:
                    logger.error(f"批量更新执行失败: {e}")
                    if conn:
                        try:
                            conn.rollback()
                        except:
                            pass
                    raise
            except Exception as e:
                logger.error(f"批量更新执行失败: {e}")
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                raise
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

