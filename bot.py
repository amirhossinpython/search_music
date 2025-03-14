import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


required_packages = [
    'rubpy',
    'requests',
    'beautifulsoup4',
    'urllib3'
]

# بررسی و نصب کتابخانه‌ها
for package in required_packages:
    try:
        __import__(package.split('>')[0].split('<')[0].split('=')[0])
    except ImportError:
        print(f"کتابخانه {package} یافت نشد. در حال نصب...")
        install_package(package)

from rubpy import Client, filters
from rubpy.types import Updates
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os

# ایجاد کلاینت ربات
bot = Client(name='search_music')

# تابع برای جستجو در سایت
def search_music(query: str):
    try:
        encoded_query = quote(query)
        search_url = f"https://sevilmusics.com/?s={encoded_query}"
        response = requests.get(search_url, timeout=10)  
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('article')
            
            if not results:
                return []
            
            music_results = []
            for result in results[:5]:  # محدود کردن نتایج به ۵ مورد
                title_tag = result.find('h2', class_='entry-title')
                title = title_tag.text.strip() if title_tag else "عنوان نامعلوم"
                
                link_tag = title_tag.find('a') if title_tag else None
                link = link_tag['href'] if link_tag else "لینک نامعلوم"
                
                date_tag = result.find('span')
                date = date_tag.text.strip() if date_tag else "تاریخ نامعلوم"
                
                image_tag = result.find('img')
                image = image_tag['src'] if image_tag else None
                
                audio_tag = result.find('audio')
                audio = audio_tag['src'] if audio_tag else None
                
                music_results.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'image': image,
                    'audio': audio
                })
            
            return music_results
        else:
            return []
    except Exception as e:
        print(f"خطا در جستجو: {e}")
        return []

# تابع برای دانلود فایل صوتی
def download_audio(url: str, filename: str):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        print(f"خطا در دانلود فایل صوتی: {e}")
        return False


@bot.on_message_updates(filters.is_private)
async def updates(message: Updates):
    query = message.text.replace("سرچ","")
    
    if message.text.startswith("سرچ"):
        await message.reply("درحال سرچ اهنگ ویاخواننده.....")
        
        try:
            results = search_music(query)
            
            if not results:
                await message.reply("هیچ نتیجه‌ای یافت نشد. 😢")
                return
            
            # ساخت کپشن برای ۵ آهنگ
            caption = "🎵 **نتایج جستجو:**\n\n"
            for i, result in enumerate(results, start=1):
                 caption += (
                   
                    f"📅 تاریخ انتشار: {result['date']}\n"
                    f"🎶 لینک پخش آنلاین: {result['audio']}\n\n"
                )
                
            
            
            image_url = results[0]['image']
            if image_url and image_url.startswith(('http://', 'https://')):
                await message.reply_photo(image_url, caption=caption)
            else:
                await message.reply(caption)
            
            
            if results[0]['audio']:
                audio_url = results[0]['audio']
                filename = "audio.mp3"
                if download_audio(audio_url, filename):
                    await message.reply_music(filename,caption=caption)
                    os.remove(filename) 
                else:
                    await message.reply("خطا در دانلود فایل صوتی. ❌")
        
        except Exception as e:
            print(f"خطا در ارسال نتایج: {e}")
            await message.reply("خطایی در پردازش درخواست شما رخ داد. لطفاً دوباره امتحان کنید. ❌")

# اجرای ربات
bot.run()
