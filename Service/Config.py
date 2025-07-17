import sys
import os
import configparser

def create_dir_temp_path():
    my_folder = os.path.join(os.environ['LOCALAPPDATA'], 'tnmhotmail')
    os.makedirs(my_folder, exist_ok=True) 
    # Ưu tiên lấy từ biến môi trường
    return my_folder
def get_profile_base_path():
    config_path = os.path.join(os.environ['LOCALAPPDATA'], 'tnmhotmail', 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    # Nếu không có profile_path trong config, dùng mặc định
    default_path = os.path.join(os.environ['LOCALAPPDATA'], 'tnmhotmail', 'profile')
    return config.get('Setting', 'profile_path', fallback=default_path)

def create_dir_path_save_profile(id):
    base_path = get_profile_base_path()
    dir_temp_profile_path = os.path.join(base_path, f'{id}')
    if not os.path.exists(dir_temp_profile_path):
        os.makedirs(dir_temp_profile_path)
    return dir_temp_profile_path
# def create_dir_path_save_profile(id):
#     base_path = create_dir_temp_path()
#     dir_temp_profile_path = os.path.join(base_path, "profile",f'{id}')
    
#     if not os.path.exists(dir_temp_profile_path):
#         os.makedirs(dir_temp_profile_path)
    
#     return dir_temp_profile_path

def create_dir_path_save_extension():
    # Chưa sử dụng, tránh lỗi import
    return None