// Creator Agent Hub - Main JavaScript
class CreatorAgentHub {
    constructor() {
        this.API_BASE = 'http://127.0.0.1:8000';
        this.currentWorkflow = {
            step: 1,
            ideas: [],
            selectedIdea: null,
            draftedContent: null,
            progress: 0
        };
        this.agents = {
            ideation: { status: 'idle', element: null },
            creation: { status: 'idle', element: null },
            publishing: { status: 'idle', element: null },
            analysis: { status: 'idle', element: null },
            sponsorship: { status: 'idle', element: null }
        };
        this.init();
    }

    init() {
        this.initializeAgents();
        this.bindEvents();
        this.updateProgress();
        this.checkAPIHealth();
    }

    initializeAgents() {
        // Initialize agent status elements
        this.agents.ideation.element = document.getElementById('ideation-agent');
        this.agents.creation.element = document.getElementById('creation-agent');
        this.agents.publishing.element = document.getElementById('publishing-agent');
        this.agents.analysis.element = document.getElementById('analysis-agent');
        this.agents.sponsorship.element = document.getElementById('sponsorship-agent');
    }

    bindEvents() {
        // Bind workflow step events
        document.addEventListener('DOMContentLoaded', () => {
            this.setupWorkflowSteps();
        });
    }

    setupWorkflowSteps() {
        // Add click handlers for workflow steps
        const steps = document.querySelectorAll('.workflow-step');
        steps.forEach((step, index) => {
            step.addEventListener('click', () => {
                this.activateStep(index + 1);
            });
        });
    }

    activateStep(stepNumber) {
        // Remove active class from all steps
        document.querySelectorAll('.workflow-step').forEach(step => {
            step.classList.remove('active');
        });

        // Add active class to current step
        const currentStep = document.querySelector(`#step-ideation, #step-creation, #step-publishing, #step-sponsorship`);
        if (currentStep) {
            currentStep.classList.add('active');
        }

        this.currentWorkflow.step = stepNumber;
        this.updateProgress();
    }

    updateProgress() {
        const progress = (this.currentWorkflow.step / 4) * 100;
        this.currentWorkflow.progress = progress;
        
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progressFill) progressFill.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `${Math.round(progress)}%`;
    }

    updateAgentStatus(agentName, status, message = '') {
        const agent = this.agents[agentName];
        if (!agent || !agent.element) return;

        // Remove all status classes
        agent.element.querySelector('.status').classList.remove('idle', 'working', 'success', 'error');
        
        // Add new status class
        agent.element.querySelector('.status').classList.add(status);
        agent.element.querySelector('.status').textContent = status.charAt(0).toUpperCase() + status.slice(1);
        
        agent.status = status;
        
        // Add message if provided
        if (message) {
            this.showNotification(message, status === 'error' ? 'error' : 'success');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    showLoading(title = 'Processing...', message = 'Please wait while the agent works on your request.') {
        const modal = document.getElementById('loading-modal');
        const titleEl = document.getElementById('loading-title');
        const messageEl = document.getElementById('loading-message');
        
        if (titleEl) titleEl.textContent = title;
        if (messageEl) messageEl.textContent = message;
        
        modal.classList.add('show');
    }

    hideLoading() {
        const modal = document.getElementById('loading-modal');
        modal.classList.remove('show');
    }

    async checkAPIHealth() {
        try {
            const response = await fetch(`${this.API_BASE}/api/health`);
            if (response.ok) {
                console.log('✅ API is healthy');
            } else {
                this.showNotification('⚠️ API server is not responding properly', 'error');
            }
        } catch (error) {
            this.showNotification('❌ Cannot connect to API server. Make sure the server is running.', 'error');
        }
    }

    // Step 1: Content Ideation
    async generateIdeas() {
        const niche = document.getElementById('niche-input').value.trim();
        const platform = document.getElementById('platform-select').value;
        const mediaUrl = document.getElementById('media-url').value.trim();
        
        if (!niche) {
            this.showNotification('Please enter your niche/topic', 'error');
            return;
        }

        this.updateAgentStatus('ideation', 'working');
        this.showLoading('Generating Ideas...', 'The Ideation Agent is brainstorming content ideas for your niche.');

        try {
            const response = await fetch(`${this.API_BASE}/api/generate-ideas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_niche: niche,
                    platform_choice: platform,
                    media_url: mediaUrl || null
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }

            const data = await response.json();
            
            if (data.ideas && Array.isArray(data.ideas)) {
                this.currentWorkflow.ideas = data.ideas;
                this.displayIdeas(data.ideas);
                this.updateAgentStatus('ideation', 'success', `Generated ${data.ideas.length} content ideas`);
                this.activateStep(2);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            console.error('Generate ideas error:', error);
            this.updateAgentStatus('ideation', 'error');
            this.showNotification(`Failed to generate ideas: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayIdeas(ideas) {
        const resultsDiv = document.getElementById('ideation-results');
        const ideaSelector = document.getElementById('idea-selector');
        
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <h4><i class="fas fa-lightbulb"></i> Generated Ideas (${ideas.length})</h4>
                <div class="ideas-grid">
                    ${ideas.map((idea, index) => `
                        <div class="idea-card" onclick="agentHub.selectIdea(${index})">
                            <h4>${idea.title}</h4>
                            <p>${idea.summary}</p>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        if (ideaSelector) {
            ideaSelector.innerHTML = '<p>Select an idea above to continue to content creation</p>';
        }
    }

    selectIdea(index) {
        this.currentWorkflow.selectedIdea = this.currentWorkflow.ideas[index];
        
        // Update UI to show selected idea
        document.querySelectorAll('.idea-card').forEach(card => card.classList.remove('selected'));
        event.target.closest('.idea-card').classList.add('selected');
        
        // Enable draft button
        const draftBtn = document.getElementById('draft-btn');
        if (draftBtn) {
            draftBtn.disabled = false;
        }
        
        this.showNotification(`Selected: ${this.currentWorkflow.selectedIdea.title}`, 'success');
    }

    // Step 2: Content Creation
    async draftContent() {
        if (!this.currentWorkflow.selectedIdea) {
            this.showNotification('Please select an idea first', 'error');
            return;
        }

        this.updateAgentStatus('creation', 'working');
        this.showLoading('Drafting Content...', 'The Creation Agent is crafting your content.');

        try {
            const response = await fetch(`${this.API_BASE}/api/draft-post`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    selected_idea: this.currentWorkflow.selectedIdea,
                    platform: document.getElementById('platform-select').value,
                    niche: document.getElementById('niche-input').value.trim(),
                    media_url: document.getElementById('media-url').value.trim() || null
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }

            const data = await response.json();
            this.currentWorkflow.draftedContent = data.post_draft;
            
            this.displayDraftedContent(data.post_draft);
            this.updateAgentStatus('creation', 'success', 'Content drafted successfully');
            this.activateStep(3);
            
            // Enable publish button
            const publishBtn = document.getElementById('publish-btn');
            if (publishBtn) {
                publishBtn.disabled = false;
            }
        } catch (error) {
            console.error('Draft content error:', error);
            this.updateAgentStatus('creation', 'error');
            this.showNotification(`Failed to draft content: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayDraftedContent(content) {
        const resultsDiv = document.getElementById('creation-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <h4><i class="fas fa-edit"></i> Drafted Content</h4>
                <div class="content-preview">
                    <pre>${content}</pre>
                </div>
            `;
        }
    }

    // Step 3: Publishing
    async publishContent() {
        if (!this.currentWorkflow.draftedContent) {
            this.showNotification('Please draft content first', 'error');
            return;
        }

        this.updateAgentStatus('publishing', 'working');
        this.showLoading('Publishing Content...', 'The Publishing Agent is publishing your content.');

        try {
            const response = await fetch(`${this.API_BASE}/api/publish`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    post_draft: this.currentWorkflow.draftedContent,
                    platform: document.getElementById('platform-select').value,
                    media_url: document.getElementById('media-url').value.trim() || null
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }

            const data = await response.json();
            this.updateAgentStatus('publishing', 'success', data.message || 'Content published successfully');
            
            this.displayPublishingResults(data);
        } catch (error) {
            console.error('Publish content error:', error);
            this.updateAgentStatus('publishing', 'error');
            this.showNotification(`Failed to publish content: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayPublishingResults(data) {
        const resultsDiv = document.getElementById('publishing-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="success-message">
                    <h4><i class="fas fa-check-circle"></i> Publishing Complete</h4>
                    <p>${data.message || 'Content has been published successfully!'}</p>
                </div>
            `;
        }
    }

    // YouTube Analysis
    analyzeYouTube() {
        const modal = document.getElementById('youtube-modal');
        modal.classList.add('show');
    }

    async analyzeYouTubeVideo() {
        const videoUrl = document.getElementById('youtube-url').value.trim();
        
        if (!videoUrl) {
            this.showNotification('Please enter a YouTube video URL', 'error');
            return;
        }

        this.updateAgentStatus('analysis', 'working');
        this.showLoading('Analyzing YouTube Comments...', 'The Analysis Agent is analyzing comments and generating insights.');

        try {
            const response = await fetch(`${this.API_BASE}/api/youtube/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_link: videoUrl })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }

            const data = await response.json();
            this.updateAgentStatus('analysis', 'success', 'Analysis completed successfully');
            
            this.displayAnalysisResults(data);
            this.closeModal('youtube-modal');
        } catch (error) {
            console.error('YouTube analysis error:', error);
            this.updateAgentStatus('analysis', 'error');
            this.showNotification(`Failed to analyze YouTube video: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayAnalysisResults(data) {
        const resultsDiv = document.getElementById('youtube-analysis-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="analysis-results">
                    <h4><i class="fas fa-chart-line"></i> Analysis Report</h4>
                    <div class="report-content">
                        <pre>${data.report}</pre>
                    </div>
                </div>
            `;
        }
    }

    // Step 4: Sponsorship
    async sendSponsorship() {
        const niche = document.getElementById('sponsorship-niche').value;
        
        if (!niche) {
            this.showNotification('Please select a target niche', 'error');
            return;
        }

        this.updateAgentStatus('sponsorship', 'working');
        this.showLoading('Sending Sponsorship Emails...', 'The Sponsorship Agent is drafting and sending emails.');

        try {
            const response = await fetch(`${this.API_BASE}/api/sponsorship/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ niche: niche })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }

            const data = await response.json();
            this.updateAgentStatus('sponsorship', 'success', `Sent ${data.emails_sent?.length || 0} sponsorship emails`);
            
            this.displaySponsorshipResults(data);
        } catch (error) {
            console.error('Sponsorship error:', error);
            this.updateAgentStatus('sponsorship', 'error');
            this.showNotification(`Failed to send sponsorship emails: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displaySponsorshipResults(data) {
        const resultsDiv = document.getElementById('sponsorship-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="success-message">
                    <h4><i class="fas fa-paper-plane"></i> Sponsorship Campaign Complete</h4>
                    <p><strong>Niche:</strong> ${data.niche}</p>
                    <p><strong>Emails Found:</strong> ${data.emails_found}</p>
                    <p><strong>Emails Sent:</strong> ${data.emails_sent?.length || 0}</p>
                    <p><strong>Message:</strong> ${data.message}</p>
                    <details>
                        <summary>Email Content</summary>
                        <pre>${data.email_content}</pre>
                    </details>
                </div>
            `;
        }
    }

    // Utility functions
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('show');
    }

    resetWorkflow() {
        this.currentWorkflow = {
            step: 1,
            ideas: [],
            selectedIdea: null,
            draftedContent: null,
            progress: 0
        };
        
        // Reset UI
        document.getElementById('niche-input').value = '';
        document.getElementById('platform-select').value = 'linkedin';
        document.getElementById('media-url').value = '';
        document.getElementById('sponsorship-niche').value = 'marketing_mails';
        
        // Clear results
        ['ideation-results', 'creation-results', 'publishing-results', 'sponsorship-results'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.innerHTML = '';
        });
        
        // Reset agent statuses
        Object.keys(this.agents).forEach(agent => {
            this.updateAgentStatus(agent, 'idle');
        });
        
        // Reset progress
        this.updateProgress();
        this.activateStep(1);
        
        this.showNotification('Workflow reset successfully', 'success');
    }
}

// Global functions for HTML onclick handlers
let agentHub;

document.addEventListener('DOMContentLoaded', () => {
    agentHub = new CreatorAgentHub();
});

// Global functions for HTML onclick handlers
function generateIdeas() {
    if (agentHub) agentHub.generateIdeas();
}

function draftContent() {
    if (agentHub) agentHub.draftContent();
}

function publishContent() {
    if (agentHub) agentHub.publishContent();
}

function analyzeYouTube() {
    if (agentHub) agentHub.analyzeYouTube();
}

function analyzeYouTubeVideo() {
    if (agentHub) agentHub.analyzeYouTubeVideo();
}

function sendSponsorship() {
    if (agentHub) agentHub.sendSponsorship();
}

function closeModal(modalId) {
    if (agentHub) agentHub.closeModal(modalId);
}

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        color: white;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 400px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification.success {
        border-color: rgba(40, 167, 69, 0.3);
        background: rgba(40, 167, 69, 0.1);
    }
    
    .notification.error {
        border-color: rgba(220, 53, 69, 0.3);
        background: rgba(220, 53, 69, 0.1);
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .notification i {
        font-size: 1.2rem;
    }
    
    .notification.success i {
        color: #28a745;
    }
    
    .notification.error i {
        color: #dc3545;
    }
    
    .content-preview {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .content-preview pre {
        color: #ffffff;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        line-height: 1.5;
    }
    
    .analysis-results {
        margin-top: 1rem;
    }
    
    .report-content {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .report-content pre {
        color: #ffffff;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        line-height: 1.5;
    }
    
    details {
        margin-top: 1rem;
    }
    
    details summary {
        cursor: pointer;
        color: #00d4ff;
        font-weight: 500;
    }
    
    details pre {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 0.5rem;
        color: #ffffff;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        line-height: 1.5;
    }
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
