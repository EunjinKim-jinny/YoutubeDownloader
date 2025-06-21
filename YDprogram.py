import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import yt_dlp
import requests
from PIL import Image
from io import BytesIO

class YouTubeThumbnailDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("유튜브 썸네일 다운로더")
        self.setFixedSize(800, 600)
        
        # 메인 위젯 생성
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # URL 입력 부분
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("유튜브 URL을 입력하세요")
        self.download_btn = QPushButton("썸네일 다운로드")
        self.download_btn.clicked.connect(self.download_thumbnail)
        self.video_download_btn = QPushButton("영상 다운로드")
        self.video_download_btn.clicked.connect(self.download_video)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.download_btn)
        url_layout.addWidget(self.video_download_btn)
        
        # 이미지 표시 레이블
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(780, 480)
        self.image_label.setStyleSheet("border: 1px solid #cccccc;")
        
        # 레이아웃에 위젯 추가
        layout.addLayout(url_layout)
        layout.addWidget(self.image_label)
        
    def download_thumbnail(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "경고", "URL을 입력해주세요!")
            return
            
        try:
            # yt-dlp를 사용하여 동영상 정보 가져오기
            ydl_opts = {}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumbnail_url = info['thumbnail']
                video_title = info['title']
                video_title = re.sub(r'[\\/:*?"<>|]', '_', video_title)
                
            # 썸네일 다운로드
            response = requests.get(thumbnail_url)
            img = Image.open(BytesIO(response.content))
            
            # 저장할 파일 이름 생성
            save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   f"{video_title}_thumbnail.jpg")
            img.save(save_path)
            
            # GUI에 썸네일 표시
            pixmap = QPixmap(save_path)
            scaled_pixmap = pixmap.scaled(780, 480, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)
            
            QMessageBox.information(self, "성공", f"썸네일이 저장되었습니다!\n저장 위치: {save_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"썸네일 다운로드 중 오류가 발생했습니다:\n{str(e)}")
            
    def download_video(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "경고", "URL을 입력해주세요!")
            return
        try:
            ydl_opts = {
                'outtmpl': os.path.join(os.path.dirname(os.path.abspath(__file__)), '%(title)s.%(ext)s'),
                'ffmpeg_location': r'C:/Users/user/ffmpeg-7.1.1-full_build/bin',
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url)
                video_title = info.get('title', 'video')
                video_title = re.sub(r'[\\/:*?"<>|]', '_', video_title)
                QMessageBox.information(self, "성공", f"영상이 다운로드되었습니다!\n저장 위치: {os.path.dirname(os.path.abspath(__file__))}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"영상 다운로드 중 오류가 발생했습니다:\n{str(e)}")

def main():
    app = QApplication(sys.argv)
    window = YouTubeThumbnailDownloader()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()