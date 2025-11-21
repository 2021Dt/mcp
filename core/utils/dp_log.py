#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dp_log.py
@Time    :   2025/02/27 15:17:29
@Author  :   dp
@DESC    :   日志初始化脚本
'''
import inspect
import sys
from pathlib import Path
from typing import Optional, Dict

from loguru import logger


class LogFactory:
    _configured_modules: Dict[str, int] = {}  # 记录模块与处理器ID的映射
    _console_handler_id: Optional[int] = None
    _default_config = {
        "log_dir": "logs",
        "retention": "7 days",
        "rotation": "00:00",
        "level": "INFO",
        "use_date_dir": True,
        "enable_console": True,
        "console_level": None,
        "compression": None,
        "enqueue": True,
        "file_format": None,
        "console_format": None,
    }

    @classmethod
    def configure_global(
        cls,
        enable_console: bool = True,
        console_level: Optional[str] = None,
        console_format: Optional[str] = None
    ):
        """全局控制台配置（只需调用一次）"""
        if enable_console and not cls._console_handler_id:
            fmt = console_format or "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan> - <level>{message}</level>"
            cls._console_handler_id = logger.add(
                sink=sys.stdout,
                level=console_level or cls._default_config["level"],
                format=fmt,
                enqueue=cls._default_config["enqueue"],
                colorize=True
            )

    @classmethod
    def get_logger(
        cls,
        module: Optional[str] = None,
        log_dir: Optional[str] = None,
        **kwargs
    ) -> logger: # type: ignore
        """
        获取模块专属logger
        :param module: 强制指定模块名（默认自动检测）
        :param log_dir: 自定义日志目录（覆盖默认）
        :param kwargs: 支持覆盖任何默认配置参数
        """
        # 自动获取调用模块名
        if not module:
            frame = inspect.stack()[1]
            module = Path(frame.filename).stem

        # 合并配置
        config = {**cls._default_config, **kwargs}  
        if log_dir:
            config["log_dir"] = log_dir

        # 如果模块未配置过，添加专属处理器
        if module not in cls._configured_modules:
            # 创建日志目录
            log_path = Path(config["log_dir"]) / module
            log_path.mkdir(parents=True, exist_ok=True)

            # 生成文件名格式
            file_name = "{time:YYYY-MM-DD}.log" if config["use_date_dir"] else "runtime.log"

            # 文件日志格式
            file_fmt = config["file_format"] or (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )

            # 添加文件处理器
            handler_id = logger.add(
                sink=str(log_path / file_name),
                rotation=config["rotation"],
                retention=config["retention"],
                compression=config["compression"],
                level=config["level"],
                format=file_fmt,
                enqueue=config["enqueue"],
                encoding="utf-8",
                filter=lambda record: record["extra"].get("module") == module
            )
            cls._configured_modules[module] = handler_id

        # 返回绑定模块的logger实例
        return logger.bind(module=module)

    @classmethod
    def remove_handler(cls, module: str):
        """移除指定模块的日志处理器"""
        if handler_id := cls._configured_modules.get(module):
            logger.remove(handler_id)
            del cls._configured_modules[module]

    @classmethod
    def disable_console(cls):
        """禁用全局控制台输出"""
        if cls._console_handler_id is not None:
            logger.remove(cls._console_handler_id)
            cls._console_handler_id = None 
