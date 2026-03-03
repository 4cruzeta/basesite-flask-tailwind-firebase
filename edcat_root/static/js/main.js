document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.querySelector('.flex-1.p-6.overflow-y-auto.space-y-4');

    chatForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const userMessage = messageInput.value.trim();

        if (userMessage) {
            // Adicionar a mensagem do usuário à UI
            appendMessage(userMessage, 'user');
            messageInput.value = '';

            try {
                // Enviar a mensagem para a API
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: userMessage }),
                });

                if (!response.ok) {
                    throw new Error(`Erro na API: ${response.statusText}`);
                }

                const data = await response.json();
                const assistantMessage = data.response;

                // Adicionar a resposta do assistente à UI
                appendMessage(assistantMessage, 'assistant');

            } catch (error) {
                console.error('Falha ao comunicar com a API:', error);
                appendMessage('Desculpe, não foi possível conectar ao assistente.', 'assistant');
            }
        }
    });

    function appendMessage(message, sender) {
        const messageWrapper = document.createElement('div');
        const messageElement = document.createElement('div');
        
        messageWrapper.className = sender === 'user' ? 'flex justify-end' : 'flex justify-start';
        messageElement.className = 'p-3 rounded-lg max-w-lg shadow-sm';
        
        if (sender === 'user') {
            messageElement.classList.add('bg-blue-500', 'text-white');
        } else {
            messageElement.classList.add('bg-gray-100', 'text-gray-800');
        }

        messageElement.innerHTML = `<p>${message}</p>`;
        messageWrapper.appendChild(messageElement);
        chatMessages.appendChild(messageWrapper);

        // Rolar para a nova mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
