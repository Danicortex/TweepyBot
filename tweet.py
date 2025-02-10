from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QLineEdit, QInputDialog, QDialog, QTextEdit, QHBoxLayout, QGridLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt
import tweepy
import os
import json
import sys

CREDENTIALS_FILE = "credentials.json"


"""RATE_LIMITS = {
    "Free": {"monthly": 1500},
    "Basic": {"monthly": 50000},
    "Pro": {"monthly": 300000}, # Assuming no practical limit
}
"""

def save_credentials():
    credentials = {
        "api_key": input("API Key: "),
        "api_secret": input("API Secret Key: "),
        "access_token": input("Access Token: "),
        "token_secret": input("Access Token Secret: "),
        "bearer_token": input("Bearer Token: "),
        "client_id": input("Client ID (Optional, press Enter to skip): ") or None,
        "client_secret": input("Client Secret (Optional, press Enter to skip): ") or None,
        "user_handle": input("Username: ")
    }
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=4)
    window.log(message="✅ Credentials saved successfully!")

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        save_credentials()
    with open(CREDENTIALS_FILE, "r") as f:
        return json.load(f)

creds = load_credentials()

client = tweepy.Client(
    bearer_token=creds["bearer_token"],
    consumer_key=creds["api_key"],
    consumer_secret=creds["api_secret"],
    access_token=creds["access_token"],
    access_token_secret=creds["token_secret"]
)

    
def tweet_media(filename, status):
    try:
        auth = tweepy.OAuth1UserHandler(
            creds["api_key"], creds["api_secret"], creds["access_token"], creds["token_secret"]
        )
        api = tweepy.API(auth)
        media = api.media_upload(filename=filename, media_category="tweet_video")
        tweet = client.create_tweet(text=f"{status} #dank #dark #funny #meme #laugh #follow #like #lol", media_ids=[media.media_id])
        tweet_id = tweet.data["id"]

        with open("tweet_video_up_save.txt", "a") as f:
            f.write(str(tweet_id) + "\n")

        window.log(message=f"✅ Tweet created: https://twitter.com/{creds['user_handle']}/status/{tweet_id}")
    except Exception as e:
        window.log(message=f"❌ Error tweeting media: {e}")

def upload_videos_from_folder(folder):
    if not os.path.exists(folder):
        window.log(message="⚠️ Folder not found!")
        return
    for video in os.listdir(folder):
        if video.endswith('.mp4'):
            video_path = os.path.join(folder, video)
            tweet_media(video_path, "Not much just another meme i enjoy watching:")

def delete_tweets(tweet_id):
    try:
        client.delete_tweet(id=tweet_id)
        window.log(message=f"✅ Tweet {tweet_id} deleted successfully!")
        return True  # ✅ Success
    except Exception as e:
        window.log(message=f"❌ Error deleting tweet {tweet_id}: {e}")
        return False  # ❌ Failure


def delete_all():
    vid_id = []
    
    # Read tweet IDs from the file
    with open("tweet_video_up_save.txt", "r") as f:
        vid_id = [line.strip() for line in f]

    if not vid_id:
        window.log(message="⚠️ No tweets found in the file.")
        return

    deleted_successfully = True  # Assume success at first

    for num in vid_id:
        try:
            x = int(num)
            success = delete_tweets(x)  # Track success/failure
            if not success:  
                deleted_successfully = False  # At least one failure occurred
        except Exception as e:
            window.log(f"❌ Failed to delete tweet {num}: {e}")
            deleted_successfully = False

    # Clear the file **only** if all deletions succeeded
    if deleted_successfully:
        with open("tweet_video_up_save.txt", "w") as w:
            w.write("")
        window.log(message="✅ All tweets deleted and file cleared successfully!")
    else:
        window.log(message="⚠️ Some tweets failed to delete. File was not cleared.")


class TwitterBotUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📢 Twitter Bot")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")

        self.setWindowIcon(QIcon("aipic.png"))

        # Set window size
        self.resize(600, 500)

        layout = QVBoxLayout()
        self.label = QLabel("📢 Twitter Bot Menu")
        self.label.setFont(QFont("Arial", 16))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.upload_btn = self.create_button("📤 Upload a Video", self.upload_video)
        self.delete_btn = self.create_button("🗑️ Delete All Tweets", self.delete_all_tweets)
        self.folder_upload_btn = self.create_button("📂 Upload All Videos from Folder", self.upload_from_folder)
        self.update_credentials_btn = self.create_button("🔑 Update API Credentials", self.update_credentials)
        self.view_ids_btn = self.create_button("📜 View Tweet IDs", self.view_tweet_ids)
        self.view_tweets_btn = self.create_button("🔍 View Tweets", self.view_tweets)
        self.exit_btn = self.create_button("🚪 Exit", self.close_app)

        layout.addWidget(self.upload_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.folder_upload_btn)
        layout.addWidget(self.update_credentials_btn)
        layout.addWidget(self.view_ids_btn)
        layout.addWidget(self.view_tweets_btn)
        layout.addWidget(self.exit_btn)
        

        # Log Output Box
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #2E2E2E; color: white; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)


    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 12))
        button.setStyleSheet(
            "background-color: #333; border-radius: 8px; padding: 10px; color: white;"
            "border: 1px solid #555;"
        )
        button.clicked.connect(callback)
        return button
    
    def log(self, message):
        """Appends log messages to the log_output widget."""
        self.log_output.append(message)
    
    def view_tweet_ids(self):
        if not os.path.exists("tweet_video_up_save.txt"):
            self.show_message("No tweet IDs found.")
            return

        with open("tweet_video_up_save.txt", "r") as f:
            tweet_ids = f.read()

        dialog = QDialog(self)
        dialog.setWindowTitle("Saved Tweet IDs")
        dialog.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        text_area = QTextEdit()
        text_area.setPlainText(tweet_ids)
        text_area.setReadOnly(True)
        text_area.setStyleSheet("background-color: #2E2E2E; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(text_area)

        dialog.setLayout(layout)
        dialog.exec()

    def show_message(self, message):
        dialog = QDialog(self)
        dialog.setWindowTitle("Message")
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec()

    def upload_video(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Video File", "", "Videos (*.mp4)")
        if file_path:
            tweet_media(file_path, "Not much just another meme i enjoy watching:")

    def delete_all_tweets(self):
        delete_all()

    def upload_from_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            upload_videos_from_folder(folder_path)

    def view_tweets(self):
        if not os.path.exists("tweet_video_up_save.txt"):
            self.show_message("No tweets found.")
            return
        
        with open("tweet_video_up_save.txt", "r") as f:
            tweet_ids = [line.strip() for line in f]

        if not tweet_ids:
            self.show_message("No tweets found.")
            return

        # Create dialog for displaying tweets
        dialog = QDialog(self)
        dialog.setWindowTitle("Saved Tweets")
        dialog.setGeometry(150, 150, 800, 600)  # Wider for side-by-side layout
        main_layout = QVBoxLayout()

        # Create grid layout for tweets (2 per row)
        grid_layout = QGridLayout()
        
        for index, tweet_id in enumerate(tweet_ids):
            tweet_url = f"https://twitter.com/{creds['user_handle']}/status/{tweet_id}"
            web_view = QWebEngineView()

            # Embed tweet properly using Twitter's embed script
            embed_code = f"""
            <html>
            <head>
                <script async src="https://platform.twitter.com/widgets.js"></script>
                <style>
                    body {{ background-color: #121212; color: white; text-align: center; }}
                    .tweet-container {{ width: 350px; height: 600px; border-radius: 10px; overflow: hidden; }}
                </style>
            </head>
            <body>
                <div class="tweet-container">
                    <blockquote class="twitter-tweet"><a href="{tweet_url}"></a></blockquote>
                </div>
            </body>
            </html>
            """

            web_view.setHtml(embed_code)

            # Place tweet into grid (2 per row)
            row = index // 2
            col = index % 2
            grid_layout.addWidget(web_view, row, col)

        # Add grid layout inside main layout
        main_layout.addLayout(grid_layout)
        dialog.setLayout(main_layout)
        dialog.exec()

    def update_credentials(self):
        save_credentials()

    def close_app(self):
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    window = TwitterBotUI()
    window.show()
    sys.exit(app.exec())
