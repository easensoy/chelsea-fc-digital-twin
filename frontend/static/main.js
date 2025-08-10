function initializeApp() {
    setupGlobalErrorHandling();
    setupToastNotifications();
    setupLoadingOverlay();
    checkAuthentication();
    initializeChartDefaults();
}

function setupGlobalErrorHandling() {
    window.addEventListener('error', function(event) {
        console.error('Global error:', event.error);
        if (event.error.message.includes('API') || event.error.message.includes('fetch')) {
            showToast('Connection error - please check your internet connection', 'error');
        }
    });

    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        event.preventDefault();
    });
}

function setupToastNotifications() {
    if (!document.getElementById('toastContainer')) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
}

function setupLoadingOverlay() {
    if (!document.getElementById('loadingOverlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Loading...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
}

function checkAuthentication() {
    const currentPath = window.location.pathname;
    const publicPaths = ['/login/', '/register/'];
    
    if (!publicPaths.includes(currentPath)) {
        fetch('/api/dashboard/widgets/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).catch(error => {
            if (error.response && error.response.status === 401) {
                window.location.href = '/login/';
            }
        });
    }
}

function initializeChartDefaults() {
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.color = '#6c757d';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 20;
        Chart.defaults.scales.linear.grid.color = 'rgba(0,0,0,0.1)';
        Chart.defaults.elements.point.radius = 4;
        Chart.defaults.elements.point.hoverRadius = 6;
        Chart.defaults.elements.line.tension = 0.4;
    }
}

function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = overlay.querySelector('p');
    
    if (loadingText) {
        loadingText.textContent = message;
    }
    
    overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('show');
    document.body.style.overflow = '';
}

function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toastId = 'toast_' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast ${type}`;
    
    const iconMap = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    
    const iconColourMap = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    toast.innerHTML = `
        <div class="toast-icon" style="color: ${iconColourMap[type]};">
            <i class="fas fa-${iconMap[type]}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="hideToast('${toastId}')">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    if (duration > 0) {
        setTimeout(() => {
            hideToast(toastId);
        }, duration);
    }
    
    return toastId;
}

function hideToast(toastId) {
    const toast = document.getElementById(toastId);
    if (!toast) return;
    
    toast.classList.remove('show');
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

function formatPlayerName(firstName, lastName) {
    return `${firstName} ${lastName}`;
}

function formatMatchScore(chelseaScore, opponentScore) {
    return `${chelseaScore}-${opponentScore}`;
}

function getPositionColour(position) {
    const colours = {
        'GK': '#ffb347',
        'CB': '#87ceeb',
        'LB': '#87ceeb', 
        'RB': '#87ceeb',
        'CDM': '#98fb98',
        'CM': '#98fb98',
        'CAM': '#98fb98',
        'LM': '#98fb98',
        'RM': '#98fb98',
        'LW': '#ffb6c1',
        'RW': '#ffb6c1',
        'ST': '#ffb6c1'
    };
    return colours[position] || '#f0f0f0';
}

function createPlayerCard(player) {
    const card = document.createElement('div');
    card.className = 'player-card';
    card.dataset.playerId = player.id;
    
    const fitnessColour = utils.getFitnessColour(player.fitness_level);
    const positionColour = getPositionColour(player.position);
    
    card.innerHTML = `
        <div class="player-card-header" style="background: linear-gradient(135deg, ${positionColour}, ${positionColour}dd);">
            <div class="player-number">${player.squad_number}</div>
            <div class="player-position">${player.position}</div>
        </div>
        <div class="player-card-body">
            <h3 class="player-name">${player.full_name}</h3>
            <div class="player-stats">
                <div class="player-stat">
                    <span class="stat-label">Age</span>
                    <span class="stat-value">${player.age}</span>
                </div>
                <div class="player-stat">
                    <span class="stat-label">Fitness</span>
                    <span class="stat-value" style="color: ${fitnessColour};">${player.fitness_level}%</span>
                </div>
                <div class="player-stat">
                    <span class="stat-label">Value</span>
                    <span class="stat-value">${utils.formatCurrency(player.market_value)}</span>
                </div>
            </div>
            ${player.is_injured ? '<div class="injury-indicator"><i class="fas fa-band-aid"></i> Injured</div>' : ''}
        </div>
        <div class="player-card-actions">
            <button class="btn btn-sm btn-primary" onclick="viewPlayerDetails('${player.id}')">
                <i class="fas fa-eye"></i> View Details
            </button>
        </div>
    `;
    
    return card;
}

function createMatchCard(match) {
    const card = document.createElement('div');
    card.className = 'match-card';
    card.dataset.matchId = match.id;
    
    const resultClass = match.result ? match.result.toLowerCase() : '';
    const resultColour = utils.getResultColour(match.result);
    
    card.innerHTML = `
        <div class="match-card-header ${resultClass}">
            <div class="match-date">${utils.formatDate(match.scheduled_datetime)}</div>
            <div class="match-type">${match.match_type}</div>
        </div>
        <div class="match-card-body">
            <div class="match-teams">
                <div class="home-team">
                    <span class="team-name">${match.is_home ? 'Chelsea' : match.opponent_name}</span>
                </div>
                <div class="match-score" style="color: ${resultColour};">
                    ${match.status === 'COMPLETED' || match.status === 'FULL_TIME' ? 
                        formatMatchScore(match.chelsea_score, match.opponent_score) : 
                        'vs'
                    }
                </div>
                <div class="away-team">
                    <span class="team-name">${match.is_home ? match.opponent_name : 'Chelsea'}</span>
                </div>
            </div>
            <div class="match-venue">${match.venue}</div>
            <div class="match-status">
                <span class="status-badge status-${match.status.toLowerCase()}">${match.status}</span>
            </div>
        </div>
        <div class="match-card-actions">
            <button class="btn btn-sm btn-primary" onclick="viewMatchDetails('${match.id}')">
                <i class="fas fa-eye"></i> View Details
            </button>
            ${match.status === 'LIVE' || match.status === 'HALF_TIME' ? 
                `<button class="btn btn-sm btn-success" onclick="openLiveMatch('${match.id}')">
                    <i class="fas fa-play"></i> Live
                </button>` : ''
            }
        </div>
    `;
    
    return card;
}

function createFormationCard(formation) {
    const card = document.createElement('div');
    card.className = 'formation-card';
    card.dataset.formationId = formation.id;
    
    card.innerHTML = `
        <div class="formation-card-header">
            <h3 class="formation-name">${formation.name}</h3>
            <div class="formation-structure">${formation.defensive_line}-${formation.midfield_line}-${formation.attacking_line}</div>
        </div>
        <div class="formation-card-body">
            <div class="formation-preview">
                <div class="formation-pitch">
                    ${formation.positions ? renderFormationPositions(formation.positions) : ''}
                </div>
            </div>
            <div class="formation-description">
                ${formation.description || utils.getFormationDescription(formation.name)}
            </div>
        </div>
        <div class="formation-card-actions">
            <button class="btn btn-sm btn-primary" onclick="editFormation('${formation.id}')">
                <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn btn-sm btn-outline" onclick="analyzeFormation('${formation.id}')">
                <i class="fas fa-chart-line"></i> Analyze
            </button>
        </div>
    `;
    
    return card;
}

function renderFormationPositions(positions) {
    return positions.map(pos => `
        <div class="position-marker" 
             style="left: ${pos.x_coordinate}%; top: ${pos.y_coordinate}%; background-color: ${getPositionColour(pos.position)};"
             title="${pos.position}">
            ${pos.position}
        </div>
    `).join('');
}

function viewPlayerDetails(playerId) {
    window.location.href = `/players/?player=${playerId}`;
}

function viewMatchDetails(matchId) {
    window.location.href = `/matches/?match=${matchId}`;
}

function openLiveMatch(matchId) {
    window.open(`/matches/?live=${matchId}`, '_blank');
}

function editFormation(formationId) {
    window.location.href = `/formations/?edit=${formationId}`;
}

function analyzeFormation(formationId) {
    window.location.href = `/analytics/?formation=${formationId}`;
}

function filterPlayers(filters) {
    const players = document.querySelectorAll('.player-card');
    
    players.forEach(card => {
        let show = true;
        
        if (filters.position && filters.position !== 'all') {
            const position = card.querySelector('.player-position').textContent;
            show = show && position === filters.position;
        }
        
        if (filters.fitness) {
            const fitnessText = card.querySelector('.stat-value').textContent;
            const fitness = parseInt(fitnessText);
            
            switch(filters.fitness) {
                case 'excellent':
                    show = show && fitness >= 90;
                    break;
                case 'good':
                    show = show && fitness >= 80 && fitness < 90;
                    break;
                case 'average':
                    show = show && fitness >= 70 && fitness < 80;
                    break;
                case 'poor':
                    show = show && fitness < 70;
                    break;
            }
        }
        
        if (filters.search) {
            const playerName = card.querySelector('.player-name').textContent.toLowerCase();
            show = show && playerName.includes(filters.search.toLowerCase());
        }
        
        card.style.display = show ? 'block' : 'none';
    });
}

function filterMatches(filters) {
    const matches = document.querySelectorAll('.match-card');
    
    matches.forEach(card => {
        let show = true;
        
        if (filters.status && filters.status !== 'all') {
            const status = card.querySelector('.status-badge').textContent;
            show = show && status.toLowerCase() === filters.status.toLowerCase();
        }
        
        if (filters.type && filters.type !== 'all') {
            const type = card.querySelector('.match-type').textContent;
            show = show && type === filters.type;
        }
        
        if (filters.venue && filters.venue !== 'all') {
            const isHome = card.innerHTML.includes('Chelsea') && card.innerHTML.includes('vs');
            show = show && ((filters.venue === 'home' && isHome) || (filters.venue === 'away' && !isHome));
        }
        
        card.style.display = show ? 'block' : 'none';
    });
}

function sortItems(container, sortBy, direction = 'asc') {
    const items = Array.from(container.children);
    
    items.sort((a, b) => {
        let aValue, bValue;
        
        switch(sortBy) {
            case 'name':
                aValue = a.querySelector('.player-name, .formation-name').textContent;
                bValue = b.querySelector('.player-name, .formation-name').textContent;
                break;
            case 'number':
                aValue = parseInt(a.querySelector('.player-number').textContent);
                bValue = parseInt(b.querySelector('.player-number').textContent);
                break;
            case 'date':
                aValue = new Date(a.querySelector('.match-date').textContent);
                bValue = new Date(b.querySelector('.match-date').textContent);
                break;
            case 'fitness':
                aValue = parseInt(a.querySelector('.stat-value').textContent);
                bValue = parseInt(b.querySelector('.stat-value').textContent);
                break;
            default:
                return 0;
        }
        
        if (direction === 'asc') {
            return aValue > bValue ? 1 : -1;
        } else {
            return aValue < bValue ? 1 : -1;
        }
    });
    
    items.forEach(item => container.appendChild(item));
}

function exportData(format, type) {
    showLoading('Preparing export...');
    
    const exportData = {
        export_type: type,
        format: format,
        timestamp: new Date().toISOString()
    };
    
    let endpoint;
    let filename;
    
    switch(format) {
        case 'csv':
            endpoint = '/api/exports/csv/';
            filename = `chelsea_fc_${type}_${new Date().toISOString().split('T')[0]}.csv`;
            break;
        case 'excel':
            endpoint = '/api/exports/excel/';
            filename = `chelsea_fc_${type}_${new Date().toISOString().split('T')[0]}.xlsx`;
            break;
        case 'powerbi':
            endpoint = '/api/exports/powerbi/';
            break;
        default:
            hideLoading();
            showToast('Unsupported export format', 'error');
            return;
    }
    
    if (format === 'powerbi') {
        apiClient.post(endpoint, exportData)
        .then(response => {
            hideLoading();
            showToast('Data exported to Power BI successfully', 'success');
        })
        .catch(error => {
            hideLoading();
            console.error('Export error:', error);
            showToast('Export failed: ' + utils.createErrorMessage(error), 'error');
        });
    } else {
        apiClient.downloadFile(endpoint, filename)
        .then(() => {
            hideLoading();
            showToast('File downloaded successfully', 'success');
        })
        .catch(error => {
            hideLoading();
            console.error('Download error:', error);
            showToast('Download failed: ' + utils.createErrorMessage(error), 'error');
        });
    }
}

function validateFormData(formData, validationRules) {
    const validation = utils.validateFormData(formData, validationRules);
    
    const existingErrors = document.querySelectorAll('.form-error');
    existingErrors.forEach(error => error.remove());
    
    if (!validation.isValid) {
        Object.keys(validation.errors).forEach(field => {
            const fieldElement = document.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'form-error';
                errorDiv.textContent = validation.errors[field];
                fieldElement.parentNode.appendChild(errorDiv);
                fieldElement.classList.add('is-invalid');
            }
        });
        
        const firstError = document.querySelector('.form-error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    return validation.isValid;
}

function clearFormErrors() {
    const errors = document.querySelectorAll('.form-error');
    errors.forEach(error => error.remove());
    
    const invalidFields = document.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => field.classList.remove('is-invalid'));
}

function handleFormSubmit(form, submitHandler) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        clearFormErrors();
        
        try {
            showLoading('Saving...');
            await submitHandler(data);
            hideLoading();
            showToast('Data saved successfully', 'success');
        } catch (error) {
            hideLoading();
            console.error('Form submission error:', error);
            showToast('Save failed: ' + utils.createErrorMessage(error), 'error');
        }
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function setupSearchFunctionality(searchInput, searchHandler) {
    const debouncedSearch = debounce(searchHandler, 300);
    searchInput.addEventListener('input', debouncedSearch);
}

function setupInfiniteScroll(container, loadMoreHandler) {
    const throttledScroll = throttle(() => {
        if (container.scrollTop + container.clientHeight >= container.scrollHeight - 100) {
            loadMoreHandler();
        }
    }, 200);
    
    container.addEventListener('scroll', throttledScroll);
}

function createPagination(totalItems, itemsPerPage, currentPage, onPageChange) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pagination = document.createElement('div');
    pagination.className = 'pagination';
    
    if (currentPage > 1) {
        const prevBtn = document.createElement('button');
        prevBtn.className = 'btn btn-outline btn-sm';
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i> Previous';
        prevBtn.onclick = () => onPageChange(currentPage - 1);
        pagination.appendChild(prevBtn);
    }
    
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `btn btn-sm ${i === currentPage ? 'btn-primary' : 'btn-outline'}`;
        pageBtn.textContent = i;
        pageBtn.onclick = () => onPageChange(i);
        pagination.appendChild(pageBtn);
    }
    
    if (currentPage < totalPages) {
        const nextBtn = document.createElement('button');
        nextBtn.className = 'btn btn-outline btn-sm';
        nextBtn.innerHTML = 'Next <i class="fas fa-chevron-right"></i>';
        nextBtn.onclick = () => onPageChange(currentPage + 1);
        pagination.appendChild(nextBtn);
    }
    
    return pagination;
}

function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            
            setTimeout(() => tooltip.classList.add('show'), 10);
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.classList.remove('show');
                setTimeout(() => {
                    if (this._tooltip && this._tooltip.parentNode) {
                        this._tooltip.parentNode.removeChild(this._tooltip);
                    }
                }, 200);
            }
        });
    });
}

window.addEventListener('load', function() {
    initializeTooltips();
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeApp,
        showLoading,
        hideLoading,
        showToast,
        hideToast,
        createPlayerCard,
        createMatchCard,
        createFormationCard,
        filterPlayers,
        filterMatches,
        exportData,
        validateFormData
    };
}