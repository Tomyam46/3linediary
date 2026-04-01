import os
from datetime import date
from flask import Flask, request, jsonify, send_from_directory
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='public')

notion = Client(auth=os.environ.get('NOTION_API_KEY'))
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/api/diary', methods=['POST'])
def save_diary():
    data = request.get_json()
    happened = (data.get('happened') or '').strip()
    felt = (data.get('felt') or '').strip()
    tomorrow = (data.get('tomorrow') or '').strip()

    if not happened or not felt or not tomorrow:
        return jsonify({'error': '3つのフィールドをすべて入力してください。'}), 400

    api_key = os.environ.get('NOTION_API_KEY')
    db_id = os.environ.get('NOTION_DATABASE_ID')
    if not api_key or not db_id:
        return jsonify({'error': '.envにNOTION_API_KEYとNOTION_DATABASE_IDを設定してください。'}), 500

    try:
        today = date.today().isoformat()  # YYYY-MM-DD

        notion.pages.create(
            parent={'database_id': db_id},
            properties={
                '今日あったこと': {
                    'rich_text': [{'text': {'content': happened}}]
                },
                '感じたこと': {
                    'rich_text': [{'text': {'content': felt}}]
                },
                '明日に向けてのひとこと': {
                    'rich_text': [{'text': {'content': tomorrow}}]
                },
                '日付': {
                    'date': {'start': today}
                }
            }
        )
        return jsonify({'success': True, 'message': '日記を保存しました！'})

    except Exception as e:
        print(f'Notion APIエラー: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'日記アプリ起動中: http://localhost:{port}')
    app.run(debug=False, port=port)
