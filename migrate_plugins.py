#!/usr/bin/env python3
"""
插件迁移脚本
将现有的 .py 插件文件迁移到按文件夹组织的新结构
"""

import os
import shutil

def migrate_plugins():
    # 源插件目录（旧结构）
    source_dir = "plugins"
    # 目标插件目录（新结构）
    target_dir = "plugins_new"
    
    if not os.path.exists(source_dir):
        print(f"源插件目录 {source_dir} 不存在")
        return
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 遍历源目录中的所有文件
    for filename in os.listdir(source_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            plugin_name = filename[:-3]  # 移除 .py 后缀
            source_file = os.path.join(source_dir, filename)
            plugin_dir = os.path.join(target_dir, plugin_name)
            
            # 创建插件目录
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)
            
            # 移动插件文件并重命名为 __init__.py
            target_file = os.path.join(plugin_dir, "__init__.py")
            shutil.copy2(source_file, target_file)
            print(f"已迁移插件: {filename} -> {plugin_dir}/__init__.py")
    
    print("插件迁移完成")

if __name__ == "__main__":
    migrate_plugins()