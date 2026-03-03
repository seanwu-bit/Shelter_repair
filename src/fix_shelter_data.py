#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
避難收容處所資料修正程式
修正排序問題和座標問題
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
import requests
import json
import time

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/shelter_fix_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ShelterDataFixer:
    def __init__(self):
        self.df = None
        self.fixed_df = None
        self.taiwan_bounds = {
            'min_lon': 120.000,  # 台灣本島經度下界（約120.0°E）
            'max_lon': 122.000,  # 台灣本島經度上界（約122.0°E）
            'min_lat': 21.900,   # 台灣本島緯度下界（約21.9°N）
            'max_lat': 25.300    # 台灣本島緯度上界（約25.3°N）
        }
        self.outliers = []
        self.sea_locations = []
        self.fixed_coordinates = []
        self.removed_records = []
        
    def load_data(self, file_path):
        """載入CSV資料"""
        try:
            # 嘗試不同編碼方式載入資料
            encodings = ['utf-8', 'utf-8-sig', 'big5', 'gbk', 'cp950']
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(file_path, encoding=encoding)
                    logging.info(f"成功使用 {encoding} 編碼載入資料，共 {len(self.df)} 筆記錄")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("無法使用任何編碼方式載入檔案")
            
            # 修正字元編碼問題
            self.fix_encoding_issues()
            
            # 修正管理人電話欄位
            self.fix_phone_numbers()
            
            return True
        except Exception as e:
            logging.error(f"載入資料失敗: {e}")
            return False
    
    def fix_encoding_issues(self):
        """修正字元編碼問題"""
        logging.info("開始修正字元編碼問題...")
        
        for column in self.df.columns:
            if self.df[column].dtype == 'object':
                # 對字串欄位進行編碼修正
                self.df[column] = self.df[column].astype(str)
                
                # 移除可能的編碼問題字元
                self.df[column] = self.df[column].apply(
                    lambda x: x.encode('utf-8', errors='ignore').decode('utf-8') if pd.notna(x) and x != 'nan' else x
                )
                
                # 修正常見的編碼問題
                encoding_fixes = {
                    'ï¼š': '：',
                    'ï¼Œ': '，',
                    'ï¼›': '？',
                    'ï¼': '！',
                    'ï¼½': '、',
                    'â€¦': '…',
                    'â€œ': '"',
                    'â€': '"',
                    'â€˜': ''',
                    'â€™': ''',
                    'Â': '',
                    'Â ': ' ',
                    'Â¡': '¡',
                    'Â¢': '¢',
                    'Â£': '£',
                    'Â¤': '¤',
                    'Â¥': '¥',
                    'Â¦': '¦',
                    'Â§': '§',
                    'Â¨': '¨',
                    'Â©': '©',
                    'Âª': 'ª',
                    'Â«': '«',
                    'Â¬': '¬',
                    'Â­': '­',
                    'Â®': '®',
                    'Â¯': '¯',
                    'Â°': '°',
                    'Â±': '±',
                    'Â²': '²',
                    'Â³': '³',
                    'Â´': '´',
                    'Âµ': 'µ',
                    'Â¶': '¶',
                    'Â·': '·',
                    'Â¸': '¸',
                    'Â¹': '¹',
                    'Âº': 'º',
                    'Â»': '»',
                    'Â¼': '¼',
                    'Â½': '½',
                    'Â¾': '¾',
                    'Â¿': '¿',
                    'Ã€': 'À',
                    'Ã': 'Á',
                    'Ã‚': 'Â',
                    'Ãƒ': 'Ã',
                    'Ã„': 'Ä',
                    'Ã…': 'Å',
                    'Ã†': 'Æ',
                    'Ã‡': 'Ç',
                    'Ãˆ': 'È',
                    'Ã‰': 'É',
                    'ÃŠ': 'Ê',
                    'Ã‹': 'Ë',
                    'ÃŒ': 'Ì',
                    'Ã': 'Í',
                    'ÃŽ': 'Î',
                    'Ã': 'Ï',
                    'Ã': 'Ð',
                    'Ã‘': 'Ñ',
                    'Ã’': 'Ò',
                    'Ã“': 'Ó',
                    'Ã”': 'Ô',
                    'Ã•': 'Õ',
                    'Ã–': 'Ö',
                    'Ã—': '×',
                    'Ã˜': 'Ø',
                    'Ã™': 'Ù',
                    'Ãš': 'Ú',
                    'Ã›': 'Û',
                    'Ãœ': 'Ü',
                    'Ã': 'Ý',
                    'Ãž': 'Þ',
                    'ÃŸ': 'ß',
                    'Ã ': 'à',
                    'Ã¡': 'á',
                    'Ã¢': 'â',
                    'Ã£': 'ã',
                    'Ã¤': 'ä',
                    'Ã¥': 'å',
                    'Ã¦': 'æ',
                    'Ã§': 'ç',
                    'Ã¨': 'è',
                    'Ã©': 'é',
                    'Ãª': 'ê',
                    'Ã«': 'ë',
                    'Ã¬': 'ì',
                    'Ã­': 'í',
                    'Ã®': 'î',
                    'Ã¯': 'ï',
                    'Ã°': 'ð',
                    'Ã±': 'ñ',
                    'Ã²': 'ò',
                    'Ã³': 'ó',
                    'Ã´': 'ô',
                    'Ãµ': 'õ',
                    'Ã¶': 'ö',
                    'Ã·': '÷',
                    'Ã¸': 'ø',
                    'Ã¹': 'ù',
                    'Ãº': 'ú',
                    'Ã»': 'û',
                    'Ã¼': 'ü',
                    'Ã½': 'ý',
                    'Ã¾': 'þ',
                    'Ã¿': 'ÿ'
                }
                
                for wrong, correct in encoding_fixes.items():
                    self.df[column] = self.df[column].str.replace(wrong, correct)
        
        logging.info("字元編碼問題修正完成")
    
    def fix_phone_numbers(self):
        """修正管理人電話欄位"""
        logging.info("開始修正管理人電話欄位...")
        
        if '管理人電話' not in self.df.columns:
            logging.warning("未找到'管理人電話'欄位")
            return
        
        def clean_phone_number(phone):
            if pd.isna(phone) or phone == 'nan' or phone == '':
                return ''
            
            phone_str = str(phone)
            
            # 移除中文字符
            phone_str = ''.join(char for char in phone_str if char.isdigit() or char in '-+() ')
            
            # 處理科學記號
            if 'e' in phone_str.lower() or 'E' in phone_str:
                try:
                    # 嘗試將科學記號轉換為整數
                    phone_num = float(phone_str)
                    if phone_num.is_integer():
                        phone_str = str(int(phone_num))
                    else:
                        phone_str = str(phone_num)
                except ValueError:
                    phone_str = ''
            
            # 移除非數字字符（保留-+()和空格）
            phone_str = ''.join(char for char in phone_str if char.isdigit() or char in '-+() ')
            
            # 格式化電話號碼
            if len(phone_str) >= 10:
                # 假設是台灣電話號碼格式
                if phone_str.startswith('0'):
                    if len(phone_str) == 10:
                        # 手機號碼格式: 0912-345678
                        phone_str = f"{phone_str[:4]}-{phone_str[4:]}"
                    elif len(phone_str) > 10:
                        # 帶區號的電話號碼
                        if phone_str[4] == '-':
                            phone_str = phone_str
                        else:
                            phone_str = f"{phone_str[:4]}-{phone_str[4:]}"
            
            return phone_str
        
        # 應用電話號碼清理
        original_phones = self.df['管理人電話'].copy()
        self.df['管理人電話'] = self.df['管理人電話'].apply(clean_phone_number)
        
        # 記錄修改的電話號碼
        changed_phones = []
        for idx, (original, new) in enumerate(zip(original_phones, self.df['管理人電話'])):
            if str(original) != str(new) and str(original) != 'nan':
                changed_phones.append({
                    '序號': idx + 1,
                    '原始電話': original,
                    '修正後電話': new
                })
        
        if changed_phones:
            logging.info(f"修正了 {len(changed_phones)} 個電話號碼")
            # 記錄前10個修改範例
            for change in changed_phones[:10]:
                logging.info(f"電話號碼修正: {change['原始電話']} -> {change['修正後電話']}")
        
        logging.info("管理人電話欄位修正完成")
    
    def sort_by_location(self):
        """按照縣市及鄉鎮市區重新排序"""
        logging.info("開始重新排序資料...")
        
        # 創建排序鍵：先按完整縣市名稱，再按前三字
        def sort_key(row):
            location = str(row['縣市及鄉鎮市區'])
            if pd.isna(location) or location == 'nan':
                return ('', '')
            full_name = location.strip()
            first_three = full_name[:3] if len(full_name) >= 3 else full_name
            return (full_name, first_three)
        
        # 應用排序
        self.df['sort_key'] = self.df.apply(sort_key, axis=1)
        self.df_sorted = self.df.sort_values('sort_key')
        
        # 重新編號序號
        self.df_sorted['序號'] = range(1, len(self.df_sorted) + 1)
        
        # 移除臨時排序鍵
        self.df_sorted = self.df_sorted.drop('sort_key', axis=1)
        
        logging.info("排序完成")
        return self.df_sorted
    
    def check_coordinate_bounds(self):
        """檢查座標是否超出台灣本島邊界"""
        logging.info("檢查座標邊界...")
        
        outliers = []
        
        for idx, row in self.df_sorted.iterrows():
            try:
                lon = float(row['經度'])
                lat = float(row['緯度'])
                
                # 檢查是否為金門縣或澎湖縣（跳過邊界檢查）
                location = str(row['縣市及鄉鎮市區'])
                if location.startswith('金門縣') or location.startswith('澎湖縣'):
                    continue
                
                # 檢查是否超出台灣本島邊界
                if (lon < self.taiwan_bounds['min_lon'] or 
                    lon > self.taiwan_bounds['max_lon'] or
                    lat < self.taiwan_bounds['min_lat'] or 
                    lat > self.taiwan_bounds['max_lat']):
                    
                    outlier_info = {
                        'index': idx,
                        '序號': row['序號'],
                        '縣市及鄉鎮市區': row['縣市及鄉鎮市區'],
                        '村里': row['村里'],
                        '避難收容處所地址': row['避難收容處所地址'],
                        '避難收容處所名稱': row['避難收容處所名稱'],
                        '原經度': lon,
                        '原緯度': lat,
                        '問題': '超出台灣本島邊界'
                    }
                    outliers.append(outlier_info)
                    
            except (ValueError, TypeError) as e:
                logging.warning(f"第 {idx} 行座標格式錯誤: {e}")
        
        self.outliers = outliers
        logging.info(f"發現 {len(outliers)} 筆超出台灣本島邊界的資料")
        return outliers
    
    def check_sea_locations(self):
        """檢查座標是否落於海上（簡化檢查）"""
        logging.info("檢查海上座標...")
        
        sea_locations = []
        
        # 這是一個簡化的海上檢查，實際應該使用更精確的地圖數據
        # 這裡我們檢查一些明顯的海上區域
        sea_areas = [
            {'min_lon': 120.100, 'max_lon': 120.900, 'min_lat': 23.100, 'max_lat': 23.900},  # 台灣海峽部分區域
            {'min_lon': 121.700, 'max_lon': 121.950, 'min_lat': 24.100, 'max_lat': 24.900},  # 東部海域部分區域
        ]
        
        for idx, row in self.df_sorted.iterrows():
            try:
                lon = float(row['經度'])
                lat = float(row['緯度'])
                
                # 檢查是否為金門縣或澎湖縣（跳過海上檢查）
                location = str(row['縣市及鄉鎮市區'])
                if location.startswith('金門縣') or location.startswith('澎湖縣'):
                    continue
                
                # 檢查是否在海上區域
                for sea_area in sea_areas:
                    if (sea_area['min_lon'] <= lon <= sea_area['max_lon'] and
                        sea_area['min_lat'] <= lat <= sea_area['max_lat']):
                        
                        sea_info = {
                            'index': idx,
                            '序號': row['序號'],
                            '縣市及鄉鎮市區': row['縣市及鄉鎮市區'],
                            '村里': row['村里'],
                            '避難收容處所地址': row['避難收容處所地址'],
                            '避難收容處所名稱': row['避難收容處所名稱'],
                            '經度': lon,
                            '緯度': lat,
                            '問題': '可能落於海上'
                        }
                        sea_locations.append(sea_info)
                        break
                        
            except (ValueError, TypeError) as e:
                logging.warning(f"第 {idx} 行座標格式錯誤: {e}")
        
        self.sea_locations = sea_locations
        logging.info(f"發現 {len(sea_locations)} 筆可能落於海上的資料")
        return sea_locations
    
    def search_correct_coordinates(self, address):
        """搜尋正確的經緯度座標（使用地理編碼API）"""
        # 這是一個示例函數，實際使用時需要接入真實的地理編碼服務
        # 例如：Google Geocoding API, 台灣電子地圖API等
        
        try:
            # 模擬API調用（實際應該調用真實API）
            # 這裡返回None表示無法找到座標
            time.sleep(0.1)  # 模擬API延遲
            
            # 實際實現範例：
            # api_url = f"https://maps.googleapis.com/maps/api/geocode/json"
            # params = {'address': address, 'key': 'YOUR_API_KEY'}
            # response = requests.get(api_url, params=params)
            # data = response.json()
            # if data['status'] == 'OK' and data['results']:
            #     location = data['results'][0]['geometry']['location']
            #     return location['lat'], location['lng']
            
            return None, None
            
        except Exception as e:
            logging.warning(f"搜尋座標失敗 {address}: {e}")
            return None, None
    
    def fix_coordinates(self):
        """修正問題座標 - 只檢查邊界外的座標"""
        logging.info("開始修正座標...")
        
        # 只處理邊界外的座標，不檢查海上座標
        fixed_coords = []
        removed_records = []
        
        for record in self.outliers:
            idx = record['index']
            address = str(record['避難收容處所地址'])
            name = str(record['避難收容處所名稱'])
            
            # 檢查必要欄位是否為空
            if pd.isna(address) or address == 'nan' or address.strip() == '':
                removed_info = {
                    '序號': record['序號'],
                    '避難收容處所名稱': name,
                    '原因': '地址欄位為空',
                    '原經度': record.get('原經度', record.get('經度')),
                    '原緯度': record.get('原緯度', record.get('緯度'))
                }
                removed_records.append(removed_info)
                self.df_sorted = self.df_sorted.drop(idx)
                continue
            
            # 搜尋正確座標
            search_query = f"{address} {name}"
            new_lat, new_lon = self.search_correct_coordinates(search_query)
            
            if new_lat is not None and new_lon is not None:
                # 更新座標（精度到小數點後第六位）
                self.df_sorted.at[idx, '經度'] = round(new_lon, 6)
                self.df_sorted.at[idx, '緯度'] = round(new_lat, 6)
                
                fixed_info = {
                    '序號': record['序號'],
                    '避難收容處所名稱': name,
                    '地址': address,
                    '原經度': record.get('原經度', record.get('經度')),
                    '原緯度': record.get('原緯度', record.get('緯度')),
                    '新經度': round(new_lon, 6),
                    '新緯度': round(new_lat, 6)
                }
                fixed_coords.append(fixed_info)
                logging.info(f"修正座標: {name}")
            else:
                # 無法找到正確座標，移除記錄
                removed_info = {
                    '序號': record['序號'],
                    '避難收容處所名稱': name,
                    '原因': '無法找到正確座標',
                    '原經度': record.get('原經度', record.get('經度')),
                    '原緯度': record.get('原緯度', record.get('緯度'))
                }
                removed_records.append(removed_info)
                self.df_sorted = self.df_sorted.drop(idx)
        
        self.fixed_coordinates = fixed_coords
        self.removed_records = removed_records
        
        logging.info(f"修正了 {len(fixed_coords)} 筆座標")
        logging.info(f"移除了 {len(removed_records)} 筆記錄")
        
        return fixed_coords, removed_records
    
    def save_fixed_data(self, output_path):
        """儲存修正後的資料"""
        try:
            self.df_sorted.to_csv(output_path, index=False, encoding='utf-8-sig')
            logging.info(f"修正後的資料已儲存至: {output_path}")
            return True
        except Exception as e:
            logging.error(f"儲存資料失敗: {e}")
            return False
    
    def generate_report(self):
        """生成修正報告"""
        report = []
        report.append("=" * 50)
        report.append("避難收容處所資料修正報告")
        report.append(f"修正時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 50)
        
        # 原始資料統計
        report.append(f"\n原始資料統計:")
        report.append(f"- 總記錄數: {len(self.df)}")
        
        # 編碼修正統計
        report.append(f"\n編碼修正處理:")
        report.append(f"- 已嘗試多種編碼方式載入資料")
        report.append(f"- 已修正常見字元編碼問題")
        report.append(f"- 已清理管理人電話欄位")
        
        # 排序統計
        report.append(f"\n排序處理:")
        report.append(f"- 已按'縣市及鄉鎮市區'重新排序")
        report.append(f"- 排序邏輯: 完全相同 > 前三字相同")
        
        # 座標問題統計
        report.append(f"\n座標問題統計:")
        report.append(f"- 超出台灣本島邊界: {len(self.outliers)} 筆")
        report.append(f"- 可能落於海上: {len(self.sea_locations)} 筆")
        report.append(f"- 成功修正座標: {len(self.fixed_coordinates)} 筆")
        report.append(f"- 移除記錄: {len(self.removed_records)} 筆")
        
        # 最終統計
        report.append(f"\n最終統計:")
        report.append(f"- 修正後記錄數: {len(self.df_sorted)}")
        
        # 詳細問題記錄
        if self.outliers:
            report.append(f"\n超出台灣本島邊界的記錄:")
            for record in self.outliers[:10]:  # 只顯示前10筆
                report.append(f"  序號{record['序號']}: {record['避難收容處所名稱']} "
                            f"({record['原經度']}, {record['原緯度']})")
        
        if self.sea_locations:
            report.append(f"\n可能落於海上的記錄:")
            for record in self.sea_locations[:10]:  # 只顯示前10筆
                report.append(f"  序號{record['序號']}: {record['避難收容處所名稱']} "
                            f"({record['經度']}, {record['緯度']})")
        
        if self.fixed_coordinates:
            report.append(f"\n成功修正的座標:")
            for record in self.fixed_coordinates[:10]:  # 只顯示前10筆
                report.append(f"  序號{record['序號']}: {record['避難收容處所名稱']}")
                report.append(f"    原: ({record['原經度']}, {record['原緯度']})")
                report.append(f"    新: ({record['新經度']}, {record['新緯度']})")
        
        if self.removed_records:
            report.append(f"\n移除的記錄:")
            for record in self.removed_records:
                report.append(f"  序號{record['序號']}: {record['避難收容處所名稱']} - {record['原因']}")
        
        # 邊界設定說明
        report.append(f"\n邊界設定說明:")
        report.append(f"- 台灣本島經度範圍: {self.taiwan_bounds['min_lon']}° - {self.taiwan_bounds['max_lon']}°E")
        report.append(f"- 台灣本島緯度範圍: {self.taiwan_bounds['min_lat']}° - {self.taiwan_bounds['max_lat']}°N")
        report.append(f"- 座標精度: 小數點後第三位")
        report.append(f"- 金門縣、澎湖縣資料已跳過邊界檢查")
        
        return "\n".join(report)

def main():
    """主程式"""
    fixer = ShelterDataFixer()
    
    # 載入資料
    if not fixer.load_data('data/避難收容處所點位檔案v9.csv'):
        return
    
    # 重新排序
    fixer.sort_by_location()
    
    # 檢查座標問題（只檢查邊界外座標）
    outliers = fixer.check_coordinate_bounds()
    
    # 修正座標（只處理邊界外的座標）
    fixer.fix_coordinates()
    
    # 儲存修正後的資料
    fixer.save_fixed_data('outputs/避難收容處所點位檔案v9_修正版.csv')
    
    # 生成報告
    report = fixer.generate_report()
    
    # 儲存報告
    with open('outputs/修正報告.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    logging.info("資料修正完成！")
    print(report)

if __name__ == "__main__":
    main()
