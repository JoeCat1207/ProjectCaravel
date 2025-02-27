document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const submitButton = document.getElementById('submit-prompt');
    const resultsContainer = document.getElementById('results');
    const parsingOutput = document.getElementById('parsing-output');
    const generalOutput = document.getElementById('general-output');
    const mathOutput = document.getElementById('math-output');
    const codingOutput = document.getElementById('coding-output');
    const literatureOutput = document.getElementById('literature-output');
    const combinedOutput = document.getElementById('combined-output');
    
    // Poll status interval in milliseconds
    const POLL_INTERVAL = 1000;
    
    let currentSessionId = null;
    let pollingInterval = null;
    
    submitButton.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        
        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }
        
        // Reset outputs
        parsingOutput.textContent = 'Parsing prompt...';
        generalOutput.textContent = '';
        mathOutput.textContent = '';
        codingOutput.textContent = '';
        literatureOutput.textContent = '';
        combinedOutput.textContent = '';
        
        // Show results container
        resultsContainer.classList.remove('hidden');
        
        try {
            // Submit prompt
            const response = await fetch('/api/prompt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });
            
            const data = await response.json();
            currentSessionId = data.session_id;
            
            // Start polling for status updates
            if (pollingInterval) {
                clearInterval(pollingInterval);
            }
            
            pollingInterval = setInterval(pollStatus, POLL_INTERVAL);
        } catch (error) {
            console.error('Error submitting prompt:', error);
            parsingOutput.textContent = 'Error: ' + error.message;
        }
    });
    
    async function pollStatus() {
        if (!currentSessionId) return;
        
        try {
            const response = await fetch(`/api/status/${currentSessionId}`);
            const data = await response.json();
            
            updateUI(data);
            
            // Stop polling when completed or error
            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(pollingInterval);
                pollingInterval = null;
            }
        } catch (error) {
            console.error('Error polling status:', error);
            parsingOutput.textContent = 'Error polling status: ' + error.message;
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }
    
    function updateUI(data) {
        // Update parsing output
        if (data.status === 'parsing') {
            parsingOutput.textContent = 'Parsing prompt...';
        } else if (data.parsed_categories) {
            parsingOutput.innerHTML = '<strong>Parsed Categories:</strong>\n\n';
            
            for (const [category, content] of Object.entries(data.parsed_categories)) {
                const formattedCategory = category.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
                parsingOutput.innerHTML += `<strong>${formattedCategory}:</strong> ${content === 'Not Applicable' ? 'Not Applicable' : 'Applicable'}\n`;
            }
        }
        
        // Update LLM outputs
        if (data.responses) {
            if (data.responses.general_knowledge) {
                generalOutput.textContent = data.responses.general_knowledge;
            }
            
            if (data.responses.mathematics) {
                mathOutput.textContent = data.responses.mathematics;
            }
            
            if (data.responses.coding) {
                codingOutput.textContent = data.responses.coding;
            }
            
            if (data.responses.literature) {
                literatureOutput.textContent = data.responses.literature;
            }
        }
        
        // Update combined response
        if (data.combined_response) {
            combinedOutput.textContent = data.combined_response;
        }
        
        // Update status messages
        const statusMessages = {
            'parsing': 'Parsing prompt with Deepseek R1 14B...',
            'generating_prompts': 'Generating optimized prompts for each category...',
            'routing_to_llms': 'Sending prompts to specialized LLMs...',
            'combining_responses': 'Combining responses from all LLMs...',
            'completed': 'Processing complete!',
            'error': 'Error: ' + (data.error || 'Unknown error')
        };
        
        if (statusMessages[data.status]) {
            const statusEl = document.createElement('div');
            statusEl.className = 'status';
            statusEl.textContent = statusMessages[data.status];
            
            // Only update if different
            const existingStatus = document.querySelector('.status');
            if (!existingStatus || existingStatus.textContent !== statusEl.textContent) {
                if (existingStatus) {
                    existingStatus.remove();
                }
                document.querySelector('.processing-step').insertBefore(statusEl, parsingOutput);
            }
        }
    }
});
