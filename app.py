import os
import pathlib
from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image, ImageDraw, ImageFont

# Define o caminho para a pasta raiz do seu projeto
BASE_DIR = pathlib.Path(__file__).parent

# Cria a instância do Flask, informando as pastas de templates e estáticos
app = Flask(__name__,
            template_folder=BASE_DIR / "templates",
            static_folder=BASE_DIR / "static")

# Configura a pasta onde as imagens serão salvas
UPLOAD_FOLDER = 'uploads'
# Cria a pasta 'uploads' se ela não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Rota para servir a página principal (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar o upload da imagem
@app.route('/upload', methods=['POST'])
def upload_file():
    # Verifica se a imagem de fundo foi enviada
    if 'background' not in request.files:
        return jsonify({'error': 'Nenhuma imagem de fundo enviada'}), 400

    background_file = request.files['background']
    object_files = request.files.getlist('objects')
    user_text = request.form.get('text', '') # Pega o texto do formulário

    if background_file.filename == '':
        return jsonify({'error': 'Nenhuma imagem de fundo selecionada'}), 400

    try:
        # --- Lógica de processamento com a Pillow ---
        
        # 1. Abre a imagem de fundo e redimensiona para um tamanho padrão
        bg_image = Image.open(background_file).convert('RGBA')
        bg_image = bg_image.resize((600, 338)) # Exemplo de tamanho para thumbnail 16:9

        # 2. Mescla as imagens de objeto (recortadas)
        # Atenção: as imagens de 'object_files' precisam ser PNGs com fundo transparente
        for i, obj_file in enumerate(object_files):
            if obj_file.filename:
                obj_image = Image.open(obj_file).convert('RGBA')
                
                # Exemplo: redimensiona e cola a imagem
                # Adiciona uma margem de acordo com a posição (i)
                margin = (i * 100) + 20
                obj_image.thumbnail((200, 200), Image.LANCZOS)
                bg_image.paste(obj_image, (bg_image.width - obj_image.width - margin, bg_image.height - obj_image.height - 20), obj_image)

        # 3. Adiciona o texto
        if user_text:
            draw = ImageDraw.Draw(bg_image)
            
            # Define a largura máxima para o texto (ex: 90% da largura da imagem)
            max_text_width = bg_image.width * 0.9
            
            # Define um tamanho de fonte inicial e a fonte que você tem
            font_size = 60
            font_path = os.path.join(app.static_folder, 'Inter_18pt-Bold.ttf')
            
            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                font = ImageFont.load_default()

            # Loop para diminuir o tamanho da fonte até que o texto caiba
            while font.getlength(user_text) > max_text_width:
                font_size -= 1
                font = ImageFont.truetype(font_path, font_size)
                
                # Garante que a fonte não fique muito pequena
                if font_size <= 20:
                    break

            # Posição do texto (centralizado horizontalmente e no topo)
            text_bbox = draw.textbbox((0, 0), user_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            # Calcula a posição central horizontalmente
            text_position_x = (bg_image.width - text_width) / 2
            
            # Define a posição vertical (por exemplo, 20 pixels do topo)
            text_position_y = 20
            
            draw.text((text_position_x, text_position_y), user_text, font=font, fill='yellow', stroke_width=2, stroke_fill='black')

        # 4. Salva a imagem final
        thumbnail_filename = 'final_thumbnail_' + background_file.filename
        thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_filename)
        bg_image.save(thumbnail_path)
        
        return jsonify({'success': True, 'thumbnail_url': f'/uploads/{thumbnail_filename}'})

    except Exception as e:
        return jsonify({'error': f'Erro no processamento da imagem: {str(e)}'}), 500

# Rota para servir os arquivos da pasta 'uploads'
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run()