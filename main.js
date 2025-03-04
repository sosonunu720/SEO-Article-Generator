
document.addEventListener('DOMContentLoaded', function() {
    const generatorForm = document.getElementById('generatorForm');
    const generateTitlesBtn = document.getElementById('generateTitlesBtn');
    const generateArticleBtn = document.getElementById('generateArticleBtn');
    const titlesContainer = document.getElementById('titlesContainer');
    const titlesList = document.querySelector('.titles-list');
    const articleContainer = document.getElementById('articleContainer');
    const generatedArticle = document.getElementById('generatedArticle');
    const loadingContainer = document.getElementById('loadingContainer');
    const loadingText = document.getElementById('loadingText');
    
    let selectedTitle = null;
    let generatedTitles = [];

    // Handle title generation form submission
    generatorForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const mainKeyword = document.getElementById('mainKeyword').value.trim();
        const seedKeywords = document.getElementById('seedKeywords').value.trim();
        
        if (!mainKeyword) {
            alert('Please enter a main keyword');
            return;
        }
        
        // Show loading
        showLoading('Generating titles...');
        
        // Clear previous titles and hide article
        titlesList.innerHTML = '';
        titlesContainer.classList.add('d-none');
        articleContainer.classList.add('d-none');
        
        try {
            const response = await fetch('/generate-titles', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    mainKeyword, 
                    seedKeywords 
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Save generated titles
                generatedTitles = data.titles;
                
                // Create title options with checkboxes
                generatedTitles.forEach((title, index) => {
                    const titleOption = document.createElement('div');
                    titleOption.className = 'title-option';
                    titleOption.setAttribute('data-index', index);
                    titleOption.innerHTML = `
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="titleRadio" 
                                id="title${index}" value="${index}">
                            <label class="form-check-label" for="title${index}">
                                ${title}
                            </label>
                        </div>
                    `;
                    titlesList.appendChild(titleOption);
                    
                    // Add click event for the entire div
                    titleOption.addEventListener('click', function() {
                        // Find the radio input and check it
                        const radio = this.querySelector('input[type="radio"]');
                        radio.checked = true;
                        
                        // Remove selected class from all options
                        document.querySelectorAll('.title-option').forEach(el => {
                            el.classList.remove('selected');
                        });
                        
                        // Add selected class to this option
                        this.classList.add('selected');
                        
                        // Save selected title
                        selectedTitle = generatedTitles[index];
                    });
                });
                
                // Show titles container
                titlesContainer.classList.remove('d-none');
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            alert('Error: Failed to connect to the server');
            console.error(error);
        } finally {
            // Hide loading
            hideLoading();
        }
    });
    
    // Handle article generation
    generateArticleBtn.addEventListener('click', async function() {
        if (!selectedTitle) {
            alert('Please select a title first');
            return;
        }
        
        const mainKeyword = document.getElementById('mainKeyword').value.trim();
        const seedKeywords = document.getElementById('seedKeywords').value.trim();
        
        // Show loading
        showLoading('Generating article...');
        
        try {
            const response = await fetch('/generate-article', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    title: selectedTitle,
                    mainKeyword, 
                    seedKeywords 
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Display the article with formatting preserved
                generatedArticle.innerHTML = data.article;
                
                // Show article container
                articleContainer.classList.remove('d-none');
                
                // Scroll to article
                articleContainer.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            alert('Error: Failed to connect to the server');
            console.error(error);
        } finally {
            // Hide loading
            hideLoading();
        }
    });
    
    // Helper functions
    function showLoading(text) {
        loadingText.textContent = text;
        loadingContainer.classList.remove('d-none');
    }
    
    function hideLoading() {
        loadingContainer.classList.add('d-none');
    }
});
