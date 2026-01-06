
from pathlib import Path

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput

BASE_DIR = Path(__file__).parent 
SOUND_FILES = {
    "bgm": BASE_DIR / "original_sound_HMusiC_1767529368504.mp3",  
    
    "click": BASE_DIR / "click.wav" 
}
class SoundManager(QObject):
    _instance = None
    POOL_SIZE = 8 

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8) 
        self.click_pool = [] 
        
        self.load_resources()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_resources(self):
        # --- Load Nhạc Nền ---
        if SOUND_FILES["bgm"].exists():
            self.player.setSource(QUrl.fromLocalFile(str(SOUND_FILES["bgm"].resolve())))
            self.player.setLoops(QMediaPlayer.Loops.Infinite)
            self.player.play()
        
        # --- Load Sound Pool (Nạp tiếng click vào 8 kênh) ---
        if SOUND_FILES["click"].exists():
            source_url = QUrl.fromLocalFile(str(SOUND_FILES["click"].resolve()))
            
            for _ in range(self.POOL_SIZE):
                effect = QSoundEffect()
                effect.setSource(source_url)
                effect.setVolume(1.0)
                self.click_pool.append(effect)
            
            print(f"✅ Đã nạp {self.POOL_SIZE} kênh âm thanh cho độ trễ bằng 0.")
        else:
            print("❌ Không tìm thấy file click.wav")

    def play_click(self):
        # KỸ THUẬT QUAN TRỌNG: Tìm kênh rảnh để phát
        for effect in self.click_pool:
            if not effect.isPlaying():
                effect.play()
                return # Tìm thấy loa rảnh, phát xong thì thoát ngay
        
        # Nếu bấm quá nhanh (cả 8 loa đều đang bận), 
        # Cưỡng chế dừng loa đầu tiên để phát đè lên (để đảm bảo luôn có tiếng)
        self.click_pool[0].stop()
        self.click_pool[0].play()
    
    def set_bgm_volume(self, val):
        self.audio_output.setVolume(val)

class SoundFilter(QObject):
    def eventFilter(self, obj, event):
        # Bắt sự kiện nhấn chuột trái
        if event.type() == QEvent.Type.MouseButtonPress:
            
            if isinstance(obj, QPushButton):
                SoundManager.instance().play_click()
    
        return False