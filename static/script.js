let generationCount = 0;
const MAX_GENERATIONS = 5;

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    
    const thumbnailImage = document.getElementById('thumbnailImage');
    const downloadButton = document.getElementById('downloadButton');
    const message = document.getElementById('message');

    // Verifica o limite de geração
    if (generationCount >= MAX_GENERATIONS) {
        document.getElementById('uploadForm').style.display = 'none'; // Esconde o formulário
        document.getElementById('adContainer').style.display = 'block'; // Mostra o espaço do anúncio
        return;
    }

    // Validação básica
    if (formData.get('background').size === 0) {
        message.textContent = 'Por favor, selecione uma imagem de fundo.';
        message.style.color = 'red';
        return;
    }
    
    message.textContent = 'Processando sua thumbnail...';
    message.style.color = 'gray';
    thumbnailImage.style.display = 'none';
    downloadButton.style.display = 'none';

    // Envia os dados para o servidor Flask
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Adiciona um parâmetro de tempo para evitar cache do navegador
            const uniqueUrl = `${data.thumbnail_url}?timestamp=${new Date().getTime()}`;
            thumbnailImage.src = uniqueUrl;
            thumbnailImage.style.display = 'block';
            downloadButton.style.display = 'inline-block';
            message.textContent = 'Sua thumbnail foi gerada com sucesso!';
            message.style.color = 'green';
            
            // Incrementa o contador após o sucesso
            generationCount++;
        } else {
            message.textContent = `Erro: ${data.error}`;
            message.style.color = 'red';
            thumbnailImage.style.display = 'none';
            downloadButton.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        message.textContent = 'Erro ao se comunicar com o servidor.';
        message.style.color = 'red';
        thumbnailImage.style.display = 'none';
        downloadButton.style.display = 'none';
    });
});

document.getElementById('downloadButton').addEventListener('click', function() {
    const imageUrl = document.getElementById('thumbnailImage').src;
    const a = document.createElement('a');
    a.href = imageUrl;
    a.download = 'thumbnail.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

// Lógica para o botão de fechar anúncio
document.getElementById('closeAdButton').addEventListener('click', function() {
    generationCount = 0; // Reseta a contagem
    document.getElementById('adContainer').style.display = 'none';
    document.getElementById('uploadForm').style.display = 'block';
});

// Lógica para mostrar o nome dos arquivos selecionados
document.getElementById('backgroundImage').addEventListener('change', function(event) {
    const fileNameSpan = document.getElementById('backgroundFileName');
    if (event.target.files.length > 0) {
        fileNameSpan.textContent = event.target.files[0].name;
    } else {
        fileNameSpan.textContent = 'Nenhum arquivo escolhido';
    }
});

document.getElementById('objectImages').addEventListener('change', function(event) {
    const fileNameSpan = document.getElementById('objectFileNames');
    if (event.target.files.length > 0) {
        let fileNames = Array.from(event.target.files).map(file => file.name).join(', ');
        fileNameSpan.textContent = fileNames;
    } else {
        fileNameSpan.textContent = 'Nenhum arquivo escolhido';
    }
});