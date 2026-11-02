class NFLBettingApp {
    constructor() {
        this.apiBase = '';
        this.autoRefreshInterval = 5 * 60 * 1000; // 5 minutes
        this.refreshTimer = null;
        this.gamesData = []; // Store all game data
        this.viewMode = 'combined'; // 'bet', 'money', or 'combined'

        // Mobile UI state
        this.isMobile = window.innerWidth <= 768;
        this.gameIndexVisible = false;

        console.log('NFL Betting App initializing...');
        this.initializeElements();
        this.bindEvents();
        this.initializeMobileFeatures();
        this.initScrollToTop();
        this.loadInitialData();
    }
    
    initializeElements() {
        console.log('Initializing DOM elements...');
        this.elements = {
            loading: document.getElementById('loading'),
            error: document.getElementById('error'),
            topConcentrations: document.getElementById('topConcentrations'),
            topConcentrationsList: document.getElementById('topConcentrationsList'),
            allGames: document.getElementById('allGames'),
            allGamesList: document.getElementById('allGamesList'),
            noGames: document.getElementById('noGames'),
            refreshBtn: document.getElementById('refreshBtn'),
            retryBtn: document.getElementById('retryBtn'),
            lastUpdate: document.getElementById('lastUpdate'),
            // Radio button toggles removed - combined view only
            topOpportunities: document.getElementById('topOpportunities'),
            topOpportunitiesList: document.getElementById('topOpportunitiesList'),
            combinedGames: document.getElementById('combinedGames'),
            combinedGamesList: document.getElementById('combinedGamesList'),
            // Mobile elements
            mobileGameIndex: document.getElementById('mobileGameIndex'),
            gameIndexList: document.getElementById('gameIndexList'),
            gamesDropdownButton: document.getElementById('gamesDropdownButton')
        };
        
        // Check if all elements were found
        for (let [key, element] of Object.entries(this.elements)) {
            if (!element) {
                console.error(`Element not found: ${key}`);
            } else {
                console.log(`Found element: ${key}`);
            }
        }
    }
    
    bindEvents() {
        this.elements.refreshBtn.addEventListener('click', () => location.reload());
        if (this.elements.retryBtn) {
            this.elements.retryBtn.addEventListener('click', () => this.loadGames());
        }

        // Mobile dropdown toggle
        if (this.elements.gamesDropdownButton) {
            this.elements.gamesDropdownButton.addEventListener('click', () => this.toggleDropdown());
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => this.handleOutsideClick(e));

        // No view mode toggle events needed - combined view only
    }

    initializeMobileFeatures() {
        console.log('Initializing mobile features...');

        // Handle window resize
        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth <= 768;
            this.updateMobileDisplay();
        });

        // Handle scroll for active game highlighting
        if (this.isMobile) {
            let scrollTimeout;
            window.addEventListener('scroll', () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    this.updateActiveGameInIndex();
                }, 100);
            });
        }
    }

    initScrollToTop() {
        const scrollBtn = document.getElementById('scrollToTop');
        if (!scrollBtn) return;

        // Show/hide button based on scroll position
        window.addEventListener('scroll', () => {
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPosition = window.scrollY;
            const tenPercentPoint = scrollHeight * 0.10;

            if (scrollPosition > tenPercentPoint) {
                scrollBtn.classList.add('visible');
            } else {
                scrollBtn.classList.remove('visible');
            }
        });

        // Scroll to top when clicked
        scrollBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    updateMobileDisplay() {
        if (this.gamesData.length > 0) {
            this.createGameIndex(); // Always create dropdown on all screen sizes
        }
    }

    createGameIndex() {
        if (!this.elements.gameIndexList) return;

        console.log('Creating game index dropdown...');
        this.elements.gameIndexList.innerHTML = '';

        // Get the currently displayed games (sorted by opportunity score)
        const gameCards = document.querySelectorAll('.combined-game-card, .game-card');

        // Process games with opportunity calculations to match what's displayed
        const gamesWithOpportunities = this.gamesData.map(game => {
            const opportunities = this.calculateGameOpportunities(game);
            return { ...game, opportunities };
        });

        // Sort games the same way they're displayed (by highest opportunity score)
        const sortedGames = gamesWithOpportunities.sort((a, b) =>
            Math.max(...a.opportunities.map(o => o.score)) - Math.max(...b.opportunities.map(o => o.score))
        ).reverse();

        sortedGames.forEach((game, displayIndex) => {
            const chip = document.createElement('div');
            chip.className = 'game-chip';
            chip.dataset.gameIndex = displayIndex; // Use display order index
            chip.dataset.gameId = this.getGameId(game);

            // Get the actual opportunity score (same as in game cards)
            const bestOpportunityScore = game.opportunities.length > 0 ?
                Math.max(...game.opportunities.map(o => o.score)) : 0;

            chip.innerHTML = `
                ${game.away_team.replace(/^.+\s/, '')} @ ${game.home_team.replace(/^.+\s/, '')}
                <span class="game-chip-score">${bestOpportunityScore}</span>
            `;

            chip.addEventListener('click', () => {
                this.scrollToGame(displayIndex); // Use display order index
                this.setActiveGameChip(chip);
                this.closeDropdown();
                this.updateDropdownButtonText(game);
            });

            this.elements.gameIndexList.appendChild(chip);
        });

        // Mobile index visibility is handled by CSS media queries
    }

    getBestOpportunityScore(game) {
        // Calculate a simple opportunity score based on betting percentages
        let maxDiff = 0;

        if (game.spread) {
            const spreadDiff = Math.abs(game.spread.away_bet_pct - game.spread.home_bet_pct);
            maxDiff = Math.max(maxDiff, spreadDiff);
        }

        if (game.totals) {
            const totalsDiff = Math.abs(game.totals.over_bet_pct - game.totals.under_bet_pct);
            maxDiff = Math.max(maxDiff, totalsDiff);
        }

        if (game.moneyline) {
            const mlDiff = Math.abs(game.moneyline.away_bet_pct - game.moneyline.home_bet_pct);
            maxDiff = Math.max(maxDiff, mlDiff);
        }

        return maxDiff + '%';
    }

    getGameId(game) {
        return `${game.away_team}-${game.home_team}`.replace(/\s+/g, '-');
    }

    scrollToGame(index) {
        const gameCards = document.querySelectorAll('.combined-game-card, .game-card');
        if (gameCards[index]) {
            // Calculate custom offset to position game title at top of visible area
            const mobileNavHeight = 90; // main padding-top for mobile
            const gameCardTop = gameCards[index].getBoundingClientRect().top + window.pageYOffset;
            const targetScrollPosition = gameCardTop - mobileNavHeight;

            window.scrollTo({
                top: targetScrollPosition,
                behavior: 'smooth'
            });
        }
    }

    setActiveGameChip(activeChip) {
        // Remove active class from all chips
        document.querySelectorAll('.game-chip').forEach(chip => {
            chip.classList.remove('active');
        });

        // Add active class to clicked chip
        activeChip.classList.add('active');
    }

    toggleDropdown() {
        if (!this.elements.gameIndexList || !this.elements.gamesDropdownButton) return;

        const isOpen = this.elements.gameIndexList.classList.contains('open');

        if (isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    openDropdown() {
        if (!this.elements.gameIndexList || !this.elements.gamesDropdownButton) return;

        this.elements.gameIndexList.classList.add('open');
        this.elements.gamesDropdownButton.classList.add('open');
    }

    closeDropdown() {
        if (!this.elements.gameIndexList || !this.elements.gamesDropdownButton) return;

        this.elements.gameIndexList.classList.remove('open');
        this.elements.gamesDropdownButton.classList.remove('open');
    }

    updateDropdownButtonText(game) {
        if (!this.elements.gamesDropdownButton) return;

        const buttonText = this.elements.gamesDropdownButton.querySelector('span');
        if (buttonText) {
            buttonText.textContent = `${game.away_team.replace(/^.+\s/, '')} @ ${game.home_team.replace(/^.+\s/, '')}`;
        }
    }

    handleOutsideClick(event) {
        if (!this.elements.mobileGameIndex) return;

        // If click is outside the mobile game index, close dropdown
        if (!this.elements.mobileGameIndex.contains(event.target)) {
            this.closeDropdown();
        }
    }

    updateActiveGameInIndex() {
        if (!this.isMobile) return;

        const gameCards = document.querySelectorAll('.combined-game-card, .game-card');
        const gameChips = document.querySelectorAll('.game-chip');

        let activeIndex = -1;
        const scrollTop = window.pageYOffset;
        const viewportHeight = window.innerHeight;

        // Find which game is currently most visible
        gameCards.forEach((card, index) => {
            const rect = card.getBoundingClientRect();
            const cardTop = rect.top + scrollTop;
            const cardBottom = cardTop + rect.height;

            // Check if card is in viewport
            if (cardTop <= scrollTop + viewportHeight * 0.5 &&
                cardBottom >= scrollTop + viewportHeight * 0.5) {
                activeIndex = index;
            }
        });

        // Update active chip
        gameChips.forEach((chip, index) => {
            chip.classList.toggle('active', index === activeIndex);
        });
    }

    
    toggleView(mode) {
        console.log(`Switching to ${mode} view mode`);
        this.viewMode = mode;
        
        // Update section headers based on view mode
        this.updateSectionHeaders();
        
        // Re-display the data with the new view mode
        if (this.gamesData && this.gamesData.length > 0) {
            if (mode === 'combined') {
                this.displayCombinedView(this.gamesData);
            } else {
                this.displayData(this.gamesData);
            }
        }
    }
    
    updateSectionHeaders() {
        const topSection = document.querySelector('#topConcentrations h2');
        const allGamesSection = document.querySelector('#allGames h2');
        
        if (topSection) {
            topSection.textContent = this.viewMode === 'bet' ? 
                'Top 5 Highest Bet Concentrations' : 
                'Top 5 Highest Money Concentrations';
        }
        
        if (allGamesSection) {
            allGamesSection.textContent = 'All Games (Sorted by Highest Concentration)';
        }
    }
    
    async loadInitialData() {
        try {
            await this.loadGames();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showError('Failed to load initial data. Trying cached data...');
            await this.loadCachedGames();
        }
    }
    
    async loadGames() {
        console.log('Loading NFL games from API...');
        this.showLoading();
        
        try {
            const url = `${this.apiBase}/api/games`;
            console.log(`Fetching from: ${url}`);
            const response = await fetch(url);
            console.log(`Response status: ${response.status}`);
            const data = await safeJson(response);
            console.log('API response:', data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            console.log(`Found ${data.games?.length || 0} NFL games`);
            this.gamesData = data.games || [];
            
            // Respect current view mode when displaying data
            if (this.viewMode === 'combined') {
                this.displayCombinedView(this.gamesData);
            } else {
                this.displayData(this.gamesData);
            }
            
            this.updateLastUpdateTime(data.timestamp);
            
            // Start auto-refresh timer after successful data load
            this.startAutoRefresh();
            
        } catch (error) {
            console.error('Error loading NFL games:', error);
            this.showError(`Failed to load NFL games: ${error.message}`);
            await this.loadCachedGames();
        }
    }
    
    async loadCachedGames() {
        try {
            const response = await fetch(`${this.apiBase}/api/games/cached`);
            const data = await safeJson(response);
            
            if (data.games && data.games.length > 0) {
                this.gamesData = data.games;
                
                // Respect current view mode when displaying cached data
                if (this.viewMode === 'combined') {
                    this.displayCombinedView(this.gamesData);
                } else {
                    this.displayData(this.gamesData);
                }
                
                this.updateLastUpdateTime(data.timestamp);
                this.showInfo('Showing cached data. Click refresh for latest data.');
                
                // Start auto-refresh timer for cached data too
                this.startAutoRefresh();
            } else {
                this.showNoGames();
            }
        } catch (error) {
            console.error('Error loading cached NFL games:', error);
            this.showNoGames();
        }
    }
    
    async refreshData() {
        this.elements.refreshBtn.disabled = true;
        this.elements.refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> REFRESHING...';
        
        try {
            const response = await fetch(`${this.apiBase}/api/refresh`);
            const result = await safeJson(response);
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            await this.loadGames();
            
        } catch (error) {
            console.error('Error refreshing NFL data:', error);
            this.showError(`Failed to refresh: ${error.message}`);
        } finally {
            this.elements.refreshBtn.disabled = false;
            this.elements.refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> REFRESH DATA';
        }
    }
    
    displayData(games) {
        console.log('Displaying data for NFL games:', games);
        this.hideAll();
        
        if (!games || games.length === 0) {
            console.log('No NFL games to display');
            this.showNoGames();
            return;
        }
        
        // Find top 5 concentrations and display them
        const topConcentrations = this.findTopConcentrations(games);
        this.displayTopConcentrations(topConcentrations);
        
        // Sort games by highest concentration and display all games
        const sortedGames = this.sortGamesByConcentration(games);
        this.displayAllGames(sortedGames);
        
        // Show both sections
        this.elements.topConcentrations.style.display = 'block';
        this.elements.allGames.style.display = 'block';
        
        console.log('NFL data display completed');
    }
    
    findTopConcentrations(games) {
        console.log('Finding top concentrations...');
        const allConcentrations = [];
        
        games.forEach(game => {
            const markets = ['moneyline', 'spread', 'totals'];
            
            markets.forEach(marketType => {
                const market = game[marketType];
                if (!market) return;
                
                if (marketType === 'totals') {
                    // Over/Under for totals
                    const overPct = this.viewMode === 'bet' ? market.over_bet_pct : market.over_money_pct;
                    const underPct = this.viewMode === 'bet' ? market.under_bet_pct : market.under_money_pct;
                    
                    if (overPct) {
                        allConcentrations.push({
                            game: game,
                            market: marketType,
                            side: 'Over',
                            percentage: overPct,
                            teamContext: `Over ${market.total_line || 'TBD'}`,
                            matchup: `${this.formatTeamName(game.away_team)} @ ${this.formatTeamName(game.home_team)}`
                        });
                    }
                    if (underPct) {
                        allConcentrations.push({
                            game: game,
                            market: marketType,
                            side: 'Under',
                            percentage: underPct,
                            teamContext: `Under ${market.total_line || 'TBD'}`,
                            matchup: `${this.formatTeamName(game.away_team)} @ ${this.formatTeamName(game.home_team)}`
                        });
                    }
                } else {
                    // Away/Home for moneyline and spread
                    const awayPct = this.viewMode === 'bet' ? market.away_bet_pct : market.away_money_pct;
                    const homePct = this.viewMode === 'bet' ? market.home_bet_pct : market.home_money_pct;
                    
                    if (awayPct) {
                        const teamContext = marketType === 'spread' && market.away_spread ? 
                            `${this.formatTeamName(game.away_team)} ${market.away_spread}` : 
                            this.formatTeamName(game.away_team);
                        
                        allConcentrations.push({
                            game: game,
                            market: marketType,
                            side: 'Away',
                            percentage: awayPct,
                            teamContext: teamContext,
                            matchup: `${this.formatTeamName(game.away_team)} @ ${this.formatTeamName(game.home_team)}`
                        });
                    }
                    if (homePct) {
                        const teamContext = marketType === 'spread' && market.home_spread ? 
                            `${this.formatTeamName(game.home_team)} ${market.home_spread}` : 
                            this.formatTeamName(game.home_team);
                        
                        allConcentrations.push({
                            game: game,
                            market: marketType,
                            side: 'Home',
                            percentage: homePct,
                            teamContext: teamContext,
                            matchup: `${this.formatTeamName(game.away_team)} @ ${this.formatTeamName(game.home_team)}`
                        });
                    }
                }
            });
        });
        
        // Sort by percentage descending and take top 5
        const topConcentrations = allConcentrations
            .sort((a, b) => b.percentage - a.percentage)
            .slice(0, 5);
            
        console.log('Top 5 NFL concentrations found:', topConcentrations);
        return topConcentrations;
    }
    
    sortGamesByConcentration(games) {
        console.log('Sorting NFL games by concentration...');
        
        const gamesWithMaxConcentration = games.map(game => {
            const markets = ['moneyline', 'spread', 'totals'];
            let maxConcentration = 0;
            
            markets.forEach(marketType => {
                const market = game[marketType];
                if (!market) return;
                
                if (marketType === 'totals') {
                    const overPct = this.viewMode === 'bet' ? (market.over_bet_pct || 0) : (market.over_money_pct || 0);
                    const underPct = this.viewMode === 'bet' ? (market.under_bet_pct || 0) : (market.under_money_pct || 0);
                    maxConcentration = Math.max(maxConcentration, overPct, underPct);
                } else {
                    const awayPct = this.viewMode === 'bet' ? (market.away_bet_pct || 0) : (market.away_money_pct || 0);
                    const homePct = this.viewMode === 'bet' ? (market.home_bet_pct || 0) : (market.home_money_pct || 0);
                    maxConcentration = Math.max(maxConcentration, awayPct, homePct);
                }
            });
            
            return { ...game, maxConcentration };
        });
        
        // Sort by max concentration descending
        const sorted = gamesWithMaxConcentration.sort((a, b) => b.maxConcentration - a.maxConcentration);
        console.log('NFL games sorted by concentration:', sorted);
        return sorted;
    }
    
    displayTopConcentrations(topConcentrations) {
        console.log('Displaying top NFL concentrations...');
        this.elements.topConcentrationsList.innerHTML = '';
        
        topConcentrations.forEach((item, index) => {
            const topItem = document.createElement('div');
            topItem.className = `top-item rank-${index + 1}`;
            
            topItem.innerHTML = `
                <div class="top-info">
                    <div class="top-matchup">${item.teamContext}</div>
                    <div class="top-market">${item.matchup} • ${item.market.toUpperCase()}</div>
                </div>
                <div class="top-percentage">
                    <div class="percentage-value">${item.percentage}%</div>
                    <div class="percentage-bar">
                        <div class="percentage-fill" style="width: ${item.percentage}%"></div>
                    </div>
                </div>
            `;
            
            this.elements.topConcentrationsList.appendChild(topItem);
        });
    }
    
    displayAllGames(games) {
        console.log('Displaying all NFL games...');
        this.elements.allGamesList.innerHTML = '';
        
        games.forEach(game => {
            const gameCard = this.createGameCard(game);
            this.elements.allGamesList.appendChild(gameCard);
        });
    }
    
    createGameCard(game) {
        const card = document.createElement('div');
        card.className = 'game-card';
        
        card.innerHTML = `
            <div class="game-header">
                <div class="game-matchup">
                    <div class="team away-team">${this.formatTeamName(game.away_team)}</div>
                    <div class="team home-team">${this.formatTeamName(game.home_team)}</div>
                </div>
                <div class="game-max-concentration">
                    <div class="max-concentration-label">Max Concentration</div>
                    <div class="max-concentration-value">${game.maxConcentration}%</div>
                </div>
            </div>
            
            <div class="game-markets">
                ${this.createMarketCard(game.moneyline, 'MONEYLINE', {
                    awayTeam: this.formatTeamName(game.away_team),
                    homeTeam: this.formatTeamName(game.home_team)
                })}
                ${this.createMarketCard(game.spread, 'SPREAD', {
                    awayTeam: this.formatTeamName(game.away_team),
                    homeTeam: this.formatTeamName(game.home_team),
                    awaySpread: game.spread?.away_spread,
                    homeSpread: game.spread?.home_spread
                })}
                ${this.createMarketCard(game.totals, 'TOTALS', {
                    awayTeam: 'OVER',
                    homeTeam: 'UNDER',
                    totalLine: game.totals?.total_line,
                    isOverUnder: true
                })}
            </div>
        `;
        
        return card;
    }
    
    createMarketCard(marketData, marketTitle, options = {}) {
        if (!marketData) {
            return `
                <div class="market-card">
                    <div class="market-title">${marketTitle}</div>
                    <div class="market-data">
                        <div class="data-row">
                            <span class="data-label">No data available</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        const isOverUnder = options.isOverUnder;
        
        // Create team headers - include spread info for spread bets
        const awayTeamHeader = marketTitle === 'SPREAD' && options.awaySpread ? 
            `${options.awayTeam} ${options.awaySpread}` : 
            options.awayTeam || 'AWAY';
        const homeTeamHeader = marketTitle === 'SPREAD' && options.homeSpread ? 
            `${options.homeTeam} ${options.homeSpread}` : 
            options.homeTeam || 'HOME';

        return `
            <div class="market-card">
                <div class="market-title">${marketTitle}</div>
                <div class="market-data">
                    <div class="team-headers">
                        <div class="team-header-spacer"></div>
                        <div class="team-header">${awayTeamHeader}</div>
                        <div class="team-header">${homeTeamHeader}</div>
                    </div>
                    
                    <div class="data-row">
                        <span class="data-label">${this.viewMode === 'bet' ? '% of Bets' : '% of Money'}</span>
                        <div class="data-values">
                            <div class="percentage ${this.getPercentageClass(isOverUnder ? 
                                (this.viewMode === 'bet' ? (marketData.over_bet_pct || 0) : (marketData.over_money_pct || 0)) : 
                                (this.viewMode === 'bet' ? (marketData.away_bet_pct || 0) : (marketData.away_money_pct || 0)))}">
                                ${isOverUnder ? 
                                    (this.viewMode === 'bet' ? (marketData.over_bet_pct || 0) : (marketData.over_money_pct || 0)) : 
                                    (this.viewMode === 'bet' ? (marketData.away_bet_pct || 0) : (marketData.away_money_pct || 0))}%
                            </div>
                            <div class="percentage ${this.getPercentageClass(isOverUnder ? 
                                (this.viewMode === 'bet' ? (marketData.under_bet_pct || 0) : (marketData.under_money_pct || 0)) : 
                                (this.viewMode === 'bet' ? (marketData.home_bet_pct || 0) : (marketData.home_money_pct || 0)))}">
                                ${isOverUnder ? 
                                    (this.viewMode === 'bet' ? (marketData.under_bet_pct || 0) : (marketData.under_money_pct || 0)) : 
                                    (this.viewMode === 'bet' ? (marketData.home_bet_pct || 0) : (marketData.home_money_pct || 0))}%
                            </div>
                        </div>
                    </div>
                    
                    <div class="data-row">
                        <span class="data-label">Odds</span>
                        <div class="odds-values">
                            <div class="odds">${this.formatOdds(isOverUnder ? marketData.over_odds : marketData.away_odds)}</div>
                            <div class="odds">${this.formatOdds(isOverUnder ? marketData.under_odds : marketData.home_odds)}</div>
                        </div>
                    </div>
                    
                    ${options.totalLine ? `
                        <div class="total-line">Total: ${options.totalLine}</div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    formatTeamName(teamName) {
        if (!teamName || teamName === 'Unknown') {
            return 'TBD';
        }

        // Team mapping for specific abbreviations that need conversion
        const teamMapping = {
            'LA': 'Los Angeles Rams',
            'JAC': 'Jacksonville Jaguars'
        };

        // Use mapping if available, otherwise return as-is
        return teamMapping[teamName] || teamName;
    }

    getTeamColor(teamName) {
        const teamColors = {
            'Arizona Cardinals': '#97233F',
            'Atlanta Falcons': '#A71930',
            'Baltimore Ravens': '#241773',
            'Buffalo Bills': '#00338D',
            'Carolina Panthers': '#0085CA',
            'Chicago Bears': '#0B162A',
            'Cincinnati Bengals': '#FB4F14',
            'Cleveland Browns': '#311D00',
            'Dallas Cowboys': '#041E42',
            'Denver Broncos': '#FB4F14',
            'Detroit Lions': '#0076B6',
            'Green Bay Packers': '#203731',
            'Houston Texans': '#03202F',
            'Indianapolis Colts': '#002C5F',
            'Jacksonville Jaguars': '#006778',
            'Kansas City Chiefs': '#E31837',
            'Las Vegas Raiders': '#000000',
            'Los Angeles Chargers': '#0080C6',
            'Los Angeles Rams': '#003594',
            'Miami Dolphins': '#008E97',
            'Minnesota Vikings': '#4F2683',
            'New England Patriots': '#002244',
            'New Orleans Saints': '#D3BC8D',
            'New York Giants': '#0B2265',
            'New York Jets': '#125740',
            'Philadelphia Eagles': '#004C54',
            'Pittsburgh Steelers': '#FFB612',
            'San Francisco 49ers': '#AA0000',
            'Seattle Seahawks': '#002244',
            'Tampa Bay Buccaneers': '#D50A0A',
            'Tennessee Titans': '#0C2340',
            'Washington Commanders': '#5A1414'
        };

        const formatted = this.formatTeamName(teamName);
        return teamColors[formatted] || '#00d4ff';
    }

    // Security: HTML escape function to prevent XSS
    escapeHtml(text) {
        if (typeof text !== 'string') return text;
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        };
        return text.replace(/[&<>"'/]/g, function (s) { return map[s]; });
    }
    
    formatOdds(odds) {
        if (!odds || odds === 'N/A') {
            return 'N/A';
        }
        // Handle special case for EVEN odds
        if (odds.toString().toUpperCase() === 'EVEN') {
            return 'EVEN';
        }
        return odds.toString().startsWith('+') || odds.toString().startsWith('-') ? odds : `+${odds}`;
    }
    
    getPercentageClass(percentage) {
        if (percentage >= 60) return 'high';
        if (percentage >= 40) return 'medium';
        return 'low';
    }
    
    updateLastUpdateTime(timestamp) {
        if (!timestamp) return;
        
        try {
            const date = new Date(timestamp);
            
            // Convert to EST timezone (America/New_York handles EST/EDT automatically)
            const timeString = date.toLocaleTimeString('en-US', {
                timeZone: 'America/New_York',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            });
            
            const updateTimeElement = this.elements.lastUpdate.querySelector('#updateTime');
            if (updateTimeElement) {
                updateTimeElement.textContent = `Last updated: ${timeString} EST`;
            }
        } catch (error) {
            console.error('Error formatting timestamp:', error);
            if (this.elements.lastUpdate.querySelector('#updateTime')) {
                this.elements.lastUpdate.querySelector('#updateTime').textContent = 'Last updated: Unknown';
            }
        }
    }
    
    showLoading() {
        this.hideAll();
        this.elements.loading.style.display = 'block';
    }
    
    showError(message) {
        this.elements.error.textContent = message;
        this.elements.error.style.display = 'block';
    }
    
    showInfo(message) {
        this.elements.error.textContent = message;
        this.elements.error.style.display = 'block';
        this.elements.error.style.backgroundColor = '#d1ecf1';
        this.elements.error.style.color = '#0c5460';
        this.elements.error.style.borderColor = '#bee5eb';
    }
    
    showNoGames() {
        this.hideAll();
        this.elements.noGames.style.display = 'block';
    }
    
    hideAll() {
        this.elements.loading.style.display = 'none';
        this.elements.error.style.display = 'none';
        this.elements.topConcentrations.style.display = 'none';
        this.elements.allGames.style.display = 'none';
        this.elements.topOpportunities.style.display = 'none';
        this.elements.combinedGames.style.display = 'none';
        this.elements.noGames.style.display = 'none';
        
        // Reset error styling
        this.elements.error.style.backgroundColor = '#f8d7da';
        this.elements.error.style.color = '#721c24';
        this.elements.error.style.borderColor = '#f5c6cb';
    }
    
    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        this.refreshTimer = setInterval(() => {
            this.loadGames();
        }, this.autoRefreshInterval);
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    // Combined View Methods
    displayCombinedView(games) {
        console.log('Displaying combined view for NFL games:', games);
        this.hideAll();
        
        if (!games || games.length === 0) {
            console.log('No NFL games to display in combined view');
            this.showNoGames();
            return;
        }
        
        // Calculate opportunity scores for all games
        const gamesWithOpportunities = games.map(game => {
            const opportunities = this.calculateGameOpportunities(game);
            return { ...game, opportunities };
        });
        
        // Find top individual opportunities across all games
        const topOpportunities = this.findTopOpportunities(gamesWithOpportunities);
        this.displayTopOpportunities(topOpportunities);
        
        // Sort games by highest opportunity score
        const sortedGames = gamesWithOpportunities.sort((a, b) => 
            Math.max(...a.opportunities.map(o => o.score)) - Math.max(...b.opportunities.map(o => o.score))
        ).reverse();
        
        this.displayCombinedGames(sortedGames);
        
        // Show both sections
        this.elements.topOpportunities.style.display = 'block';
        this.elements.combinedGames.style.display = 'block';

        // Initialize mobile features after data is displayed
        this.updateMobileDisplay();

        console.log('NFL combined view display completed');
    }
    
    calculateGameOpportunities(game) {
        const opportunities = [];
        const markets = ['moneyline', 'spread', 'totals'];
        
        markets.forEach(marketType => {
            const market = game[marketType];
            if (!market) return;
            
            if (marketType === 'totals') {
                // Over/Under analysis
                const overOpportunity = this.calculateOpportunityScore(
                    market.over_bet_pct || 0, 
                    market.over_money_pct || 0,
                    game,
                    marketType,
                    'Over',
                    market.over_odds,
                    market.total_line
                );
                
                const underOpportunity = this.calculateOpportunityScore(
                    market.under_bet_pct || 0, 
                    market.under_money_pct || 0,
                    game,
                    marketType,
                    'Under',
                    market.under_odds,
                    market.total_line
                );
                
                if (overOpportunity.score > 0) opportunities.push(overOpportunity);
                if (underOpportunity.score > 0) opportunities.push(underOpportunity);
            } else {
                // Away/Home analysis
                const awayOpportunity = this.calculateOpportunityScore(
                    market.away_bet_pct || 0, 
                    market.away_money_pct || 0,
                    game,
                    marketType,
                    'Away',
                    market.away_odds,
                    marketType === 'spread' ? market.away_spread : null
                );
                
                const homeOpportunity = this.calculateOpportunityScore(
                    market.home_bet_pct || 0, 
                    market.home_money_pct || 0,
                    game,
                    marketType,
                    'Home',
                    market.home_odds,
                    marketType === 'spread' ? market.home_spread : null
                );
                
                if (awayOpportunity.score > 0) opportunities.push(awayOpportunity);
                if (homeOpportunity.score > 0) opportunities.push(homeOpportunity);
            }
        });
        
        return opportunities;
    }

    parseAmericanOdds(oddsString) {
        if (!oddsString || oddsString === 'N/A') return null;
        const cleanOdds = oddsString.toString().replace(/[^-+0-9]/g, '');
        const numericOdds = parseInt(cleanOdds);
        return isNaN(numericOdds) ? null : numericOdds;
    }

    isMoneylineInAcceptableRange(odds) {
        const numericOdds = this.parseAmericanOdds(odds);
        if (numericOdds === null) return true; // If we can't parse, don't filter
        return numericOdds >= -200 && numericOdds <= 200;
    }

    calculateOpportunityScore(betPct, moneyPct, game, marketType, side, odds, spread) {
        // NEW SIMPLE FORMULA: Score based on sharp/public divergence (gap)
        // Matches backend: score = min(100, gap * 2) if gap >= 10% else 0

        const gap = Math.abs(betPct - moneyPct);
        let score = gap >= 10 ? Math.min(100, gap * 2) : 0;

        // Determine sharp side (where the money is)
        const sharpSide = moneyPct > betPct ? 'money-heavy' : 'bet-heavy';
        const isSharpOnThisSide = moneyPct > betPct;

        // For display, use the recommended side's percentages
        let displayBetPct = betPct;
        let displayMoneyPct = moneyPct;

        // If sharp money is on opposite side, swap to show those percentages
        if (!isSharpOnThisSide) {
            const market = game[marketType];
            if (market) {
                if (marketType === 'totals') {
                    // For totals: swap Over <-> Under
                    displayBetPct = side === 'Over' ? (market.under_bet_pct || 0) : (market.over_bet_pct || 0);
                    displayMoneyPct = side === 'Over' ? (market.under_money_pct || 0) : (market.over_money_pct || 0);
                } else {
                    // For spread/moneyline: swap Away <-> Home
                    displayBetPct = side === 'Away' ? (market.home_bet_pct || 0) : (market.away_bet_pct || 0);
                    displayMoneyPct = side === 'Away' ? (market.home_money_pct || 0) : (market.away_money_pct || 0);
                }
            }
        }

        // Get market-specific emoji
        const marketEmoji = marketType === 'spread' ? '📈' :
                           marketType === 'totals' ? '🎯' :
                           marketType === 'moneyline' ? '💰' : '🎯';

        // Determine opportunity type and description based on score
        let type = 'balanced';
        let description = '';
        let icon = '⚖️';

        if (score >= 60) {
            type = 'sharp-divergence-high';
            icon = '💎';
            const sharpBetSide = isSharpOnThisSide ? this.getTeamOrSide(game, marketType, side, spread) : this.getOppositeSide(game, marketType, side, spread);
            const publicSide = !isSharpOnThisSide ? this.getTeamOrSide(game, marketType, side, spread) : this.getOppositeSide(game, marketType, side, spread);
            description = `${marketEmoji} BET: ${sharpBetSide} (${displayMoneyPct.toFixed(0)}% sharp money vs ${displayBetPct.toFixed(0)}% public bets)`;
        } else if (score >= 30) {
            type = 'sharp-divergence';
            icon = '🤑';
            const sharpBetSide = isSharpOnThisSide ? this.getTeamOrSide(game, marketType, side, spread) : this.getOppositeSide(game, marketType, side, spread);
            description = `${marketEmoji} BET: ${sharpBetSide} (Sharp money divergence: ${gap.toFixed(1)}% gap)`;
        } else if (score >= 20) {
            type = 'minor-edge';
            icon = '📈';
            const sharpBetSide = isSharpOnThisSide ? this.getTeamOrSide(game, marketType, side, spread) : this.getOppositeSide(game, marketType, side, spread);
            description = `${marketEmoji} BET: ${sharpBetSide} (Minor sharp money edge detected)`;
        }

        return {
            game,
            marketType,
            side,
            betPct: displayBetPct,
            moneyPct: displayMoneyPct,
            odds,
            spread,
            score: Math.round(score),
            type,
            icon,
            description,
            gap,
            sharpSide,
            recommendedSide: !isSharpOnThisSide ?
                (marketType === 'totals'
                    ? (side === 'Over' ? 'Under' : 'Over')
                    : (side === 'Away' ? 'Home' : 'Away')
                ) : side
        };
    }
    
    getTeamOrSide(game, marketType, side, spread) {
        if (marketType === 'totals') {
            return side === 'Over' ? `Over ${spread || 'TBD'}` : `Under ${spread || 'TBD'}`;
        }

        const teamName = side === 'Away' ?
            this.formatTeamName(game.away_team) :
            this.formatTeamName(game.home_team);

        if (marketType === 'spread' && spread) {
            return `${teamName} ${spread}`;
        }

        return teamName;
    }

    getOppositeSide(game, marketType, side, spread) {
        if (marketType === 'totals') {
            return side === 'Over' ? `Under ${spread || 'TBD'}` : `Over ${spread || 'TBD'}`;
        }

        const oppositeTeamName = side === 'Away' ?
            this.formatTeamName(game.home_team) :
            this.formatTeamName(game.away_team);

        if (marketType === 'spread' && spread) {
            // For spread, we need to get the opposite spread value
            const oppositeSpread = side === 'Away' ?
                (game.spread?.home_spread || 'TBD') :
                (game.spread?.away_spread || 'TBD');
            return `${oppositeTeamName} ${oppositeSpread}`;
        }

        return oppositeTeamName;
    }
    
    findTopOpportunities(gamesWithOpportunities) {
        const gameOpportunityMap = new Map();
        
        // For each game, keep only the highest scoring opportunity
        gamesWithOpportunities.forEach(game => {
            const gameKey = `${game.away_team}_${game.home_team}`;
            if (game.opportunities && game.opportunities.length > 0) {
                const bestOpp = game.opportunities.reduce((best, opp) => 
                    opp.score > best.score ? opp : best
                );
                
                // Only include opportunities with meaningful scores
                if (bestOpp.score > 0) {
                    gameOpportunityMap.set(gameKey, bestOpp);
                }
            }
        });
        
        // Return top 6 opportunities, sorted by score descending
        const count = 6;
        return Array.from(gameOpportunityMap.values())
            .sort((a, b) => b.score - a.score)
            .slice(0, count);
    }
    
    displayTopOpportunities(opportunities) {
        this.elements.topOpportunitiesList.innerHTML = '';

        // Build opportunity items HTML
        const opportunitiesHTML = opportunities.map((opp, index) => `
            <div class="opportunity-item">
                <div class="opportunity-score">${opp.score}</div>
                <div class="opportunity-type ${opp.type}">
                    <span>${opp.icon}</span>
                    <span>${opp.type.replace('-', ' ').toUpperCase()}</span>
                </div>

                <div class="opportunity-details">
                    <div class="opportunity-matchup">
                        ${this.formatTeamName(opp.game.away_team)} @ ${this.formatTeamName(opp.game.home_team)}
                    </div>
                    <div class="opportunity-market">
                        ${opp.marketType.toUpperCase()} ${opp.marketType === 'spread' && opp.spread ? `(${opp.spread})` : ''}
                    </div>
                </div>

                <div class="opportunity-explanation">
                    <div class="explanation-text">${this.escapeHtml(opp.description)}</div>
                    <div class="bet-money-comparison">
                        <span>🎯 ${opp.betPct}% of bets</span>
                        <span>💰 ${opp.moneyPct}% of money</span>
                        <span>Gap: ${opp.gap.toFixed(1)}%</span>
                    </div>
                </div>

                <div class="odds-display">
                    ${this.getRecommendedBetText(opp)}
                </div>
            </div>
        `).join('');

        // Wrap in carousel on mobile, standard list on desktop
        if (this.isMobile) {
            // Create pagination dots
            const paginationDots = opportunities.map((_, index) =>
                `<span class="dot ${index === 0 ? 'active' : ''}" data-index="${index}"></span>`
            ).join('');

            this.elements.topOpportunitiesList.innerHTML = `
                <div class="opportunities-carousel-wrapper">
                    <div class="opportunities-list carousel">
                        ${opportunitiesHTML}
                    </div>
                    <div class="carousel-pagination">
                        ${paginationDots}
                    </div>
                </div>
            `;
        } else {
            this.elements.topOpportunitiesList.innerHTML = opportunitiesHTML;
        }
    }
    
    displayCombinedGames(games) {
        this.elements.combinedGamesList.innerHTML = '';

        games.forEach(game => {
            const gameCard = this.createCombinedGameCard(game);
            this.elements.combinedGamesList.appendChild(gameCard);
        });

        // Initialize carousels on mobile
        if (this.isMobile) {
            this.initializeCarousels();
            this.initializeOpportunitiesCarousel();
        }
    }
    
    createCombinedGameCard(game) {
        const card = document.createElement('div');
        card.className = 'combined-game-card';

        // Find best opportunity for this game
        const bestOpp = game.opportunities.length > 0 ?
            game.opportunities.reduce((best, opp) => opp.score > best.score ? opp : best) :
            { score: 0, description: 'No significant opportunities' };

        const overallScore = bestOpp.score;
        const scoreLevel = overallScore >= 60 ? 'high' : overallScore >= 30 ? 'medium' : 'low';
        const scoreIcon = overallScore >= 60 ? '🟢' : overallScore >= 30 ? '🟡' : '🔴';

        // Get market-specific emoji for best opportunity
        const marketEmoji = bestOpp.marketType === 'spread' ? '📈' :
                           bestOpp.marketType === 'totals' ? '🎯' :
                           bestOpp.marketType === 'moneyline' ? '💰' : '💡';

        // Generate market analysis HTML
        const marketsHTML = `
            ${this.createMarketAnalysis(game.spread, 'spread', '📈', {
                awayTeam: this.formatTeamName(game.away_team),
                homeTeam: this.formatTeamName(game.home_team),
                awaySpread: game.spread?.away_spread,
                homeSpread: game.spread?.home_spread,
                awayTeamRaw: game.away_team,
                homeTeamRaw: game.home_team
            }, game.opportunities)}
            ${this.createMarketAnalysis(game.totals, 'totals', '🎯', {
                awayTeam: 'OVER',
                homeTeam: 'UNDER',
                totalLine: game.totals?.total_line,
                isOverUnder: true
            }, game.opportunities)}
            ${this.createMarketAnalysis(game.moneyline, 'moneyline', '💰', {
                awayTeam: this.formatTeamName(game.away_team),
                homeTeam: this.formatTeamName(game.home_team),
                awayTeamRaw: game.away_team,
                homeTeamRaw: game.home_team
            }, game.opportunities)}
        `;

        // Wrap in carousel on mobile, standard grid on desktop
        const marketsContainer = this.isMobile ? `
            <div class="market-carousel-wrapper">
                <div class="markets-analysis carousel">
                    ${marketsHTML}
                </div>
                <div class="carousel-pagination">
                    <span class="dot active" data-index="0"></span>
                    <span class="dot" data-index="1"></span>
                    <span class="dot" data-index="2"></span>
                </div>
            </div>
        ` : `
            <div class="markets-analysis">
                ${marketsHTML}
            </div>
        `;

        card.innerHTML = `
            <div class="combined-game-header">
                <div class="combined-matchup">
                    <div class="combined-teams">
                        ${this.formatTeamName(game.away_team)} @ ${this.formatTeamName(game.home_team)}
                    </div>
                    <div class="best-opportunity">
                        ${marketEmoji} Best opportunity (${bestOpp.marketType ? bestOpp.marketType.toUpperCase() : 'UNKNOWN'}): ${this.escapeHtml(bestOpp.description)}
                    </div>
                </div>
                <div class="opportunity-badge ${scoreLevel}">
                    <span>${scoreIcon}</span>
                    <span>${scoreLevel.toUpperCase()}</span>
                    <span>${overallScore}</span>
                </div>
            </div>

            ${marketsContainer}
        `;

        return card;
    }
    
    createMarketAnalysis(marketData, marketType, icon, options = {}, opportunities = []) {
        if (!marketData) {
            return `
                <div class="market-analysis">
                    <div class="market-analysis-header">
                        <div class="market-icon-title">
                            <span>${icon}</span>
                            <span>${marketType.toUpperCase()}</span>
                        </div>
                        <div class="market-opportunity-level low">NO DATA</div>
                    </div>
                    <div class="market-summary">
                        <div class="summary-text">No data available</div>
                    </div>
                </div>
            `;
        }
        
        const isOverUnder = options.isOverUnder;
        
        // Get the data for both sides
        const side1BetPct = isOverUnder ? (marketData.over_bet_pct || 0) : (marketData.away_bet_pct || 0);
        const side1MoneyPct = isOverUnder ? (marketData.over_money_pct || 0) : (marketData.away_money_pct || 0);
        const side2BetPct = isOverUnder ? (marketData.under_bet_pct || 0) : (marketData.home_bet_pct || 0);
        const side2MoneyPct = isOverUnder ? (marketData.under_money_pct || 0) : (marketData.home_money_pct || 0);
        
        // Find the best opportunity score for this specific market type
        const marketOpportunities = opportunities.filter(opp => opp.marketType === marketType);
        let opportunityLevel = 'low';
        let maxScore = 0;
        
        if (marketOpportunities.length > 0) {
            maxScore = Math.max(...marketOpportunities.map(opp => opp.score));
            opportunityLevel = maxScore >= 60 ? 'high' : maxScore >= 30 ? 'medium' : 'low';
        } else {
            // Fall back to gap-based calculation if no opportunities found
            const maxGap = Math.max(
                Math.abs(side1BetPct - side1MoneyPct),
                Math.abs(side2BetPct - side2MoneyPct)
            );
            opportunityLevel = maxGap >= 20 ? 'high' : maxGap >= 10 ? 'medium' : 'low';
        }
        
        // Create labels
        let side1Label, side2Label;
        if (marketType === 'totals' && options.totalLine) {
            side1Label = `${options.awayTeam} ${options.totalLine}`;
            side2Label = `${options.homeTeam} ${options.totalLine}`;
        } else if (marketType === 'spread' && options.awaySpread) {
            side1Label = `${options.awayTeam} ${options.awaySpread}`;
            side2Label = `${options.homeTeam} ${options.homeSpread}`;
        } else {
            side1Label = options.awayTeam;
            side2Label = options.homeTeam;
        }
        
        // Get team colors if available
        const side1Color = options.awayTeamRaw && !isOverUnder ? this.getTeamColor(options.awayTeamRaw) : '#00d4ff';
        const side2Color = options.homeTeamRaw && !isOverUnder ? this.getTeamColor(options.homeTeamRaw) : '#00d4ff';

        // Get smart summary
        const summary = this.getMarketSummary(side1BetPct, side1MoneyPct, side2BetPct, side2MoneyPct, side1Label, side2Label);

        return `
            <div class="market-analysis">
                <div class="market-analysis-header">
                    <div class="market-icon-title">
                        <span>${icon}</span>
                        <span>${marketType.toUpperCase()}</span>
                    </div>
                    <div class="market-opportunity-level ${opportunityLevel}">${opportunityLevel.toUpperCase()}</div>
                </div>

                <div class="split-bar-container">
                    <div class="split-bar-label">
                        <span>${side1Label}</span>
                        <span>${side2Label}</span>
                    </div>
                    <div class="split-bar">
                        <div class="bet-bar" style="width: ${side1BetPct}%; background: ${side1Color};">
                            ${side1BetPct >= (this.isMobile ? 35 : 25) ? `${side1BetPct}% bets` : ''}
                        </div>
                        <div class="money-bar" style="width: ${side1MoneyPct}%; background: ${side1Color}; opacity: 0.7;">
                            ${side1MoneyPct >= (this.isMobile ? 35 : 25) ? `${side1MoneyPct}% money` : ''}
                        </div>
                        <div class="gap-indicator ${this.getGapClass(side1BetPct, side1MoneyPct)}">
                            ${this.getGapIndicator(side1BetPct, side1MoneyPct)}
                        </div>
                        ${side1BetPct < (this.isMobile ? 35 : 25) ? `
                            <div class="external-bet-text" style="left: ${Math.max(side1BetPct + 3, 8)}%">
                                ${side1BetPct}% bets
                            </div>
                        ` : ''}
                        ${side1MoneyPct < (this.isMobile ? 35 : 25) ? `
                            <div class="external-money-text" style="left: ${Math.max(side1MoneyPct + 3, 8)}%">
                                ${side1MoneyPct}% money
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="market-summary">
                    <div class="summary-text">${summary}</div>
                </div>
                
                <div class="odds-section">
                    <div class="odds-item">
                        ${this.formatOdds(isOverUnder ? marketData.over_odds : marketData.away_odds)}
                    </div>
                    <div class="odds-item">
                        ${this.formatOdds(isOverUnder ? marketData.under_odds : marketData.home_odds)}
                    </div>
                </div>
            </div>
        `;
    }
    
    getMarketSummary(bet1, money1, bet2, money2, label1, label2) {
        // Priority 1: Check for sharp money divergence FIRST (>10% gap between bet% and money%)
        const gap1 = Math.abs(bet1 - money1);
        const gap2 = Math.abs(bet2 - money2);
        const maxGap = Math.max(gap1, gap2);

        if (maxGap >= 10) {
            if (gap1 > gap2) {
                if (money1 > bet1) {
                    return `Sharp money likes ${label1} (${gap1.toFixed(0)}% gap)`;
                } else {
                    return `Public betting heavy on ${label1} (${gap1.toFixed(0)}% gap)`;
                }
            } else {
                if (money2 > bet2) {
                    return `Sharp money likes ${label2} (${gap2.toFixed(0)}% gap)`;
                } else {
                    return `Public betting heavy on ${label2} (${gap2.toFixed(0)}% gap)`;
                }
            }
        }

        // Priority 2: Check for heavy concentration (>70% on either side)
        const side1Max = Math.max(bet1, money1);
        const side2Max = Math.max(bet2, money2);

        if (side1Max >= 70) {
            return `Heavy action on ${label1} (${side1Max.toFixed(0)}%)`;
        }
        if (side2Max >= 70) {
            return `Heavy action on ${label2} (${side2Max.toFixed(0)}%)`;
        }

        // Priority 3: Balanced action (everything else)
        return "Balanced action on both sides";
    }
    
    getGapClass(betPct, moneyPct) {
        const gap = Math.abs(betPct - moneyPct);
        if (gap < 10) return 'balanced';
        return moneyPct > betPct ? 'sharp-money' : 'public-heavy';
    }
    
    getGapIndicator(betPct, moneyPct) {
        const gap = Math.abs(betPct - moneyPct);
        if (gap < 10) return '⚖️';
        if (moneyPct > betPct) return '🤑';
        return '🎯';
    }

    getRecommendedBetText(opp) {
        // For contrarian-heavy opportunities, show the complete bet recommendation for the opposite side (the side we actually want to bet)
        // For all other opportunity types, show the complete bet recommendation for the identified side

        if (opp.type === 'contrarian-heavy') {
            // We want to bet AGAINST the heavy public action, so get opposite side recommendation
            const market = opp.game[opp.marketType];
            if (!market) return `Recommended Bet: ${this.formatOdds(opp.odds)}`;

            if (opp.marketType === 'totals') {
                // For totals: if opportunity is on Over, recommend Under (and vice versa)
                if (opp.side === 'Over') {
                    return `Recommended Bet: Under ${opp.spread || 'TBD'} ${this.formatOdds(market.under_odds)}`;
                } else {
                    return `Recommended Bet: Over ${opp.spread || 'TBD'} ${this.formatOdds(market.over_odds)}`;
                }
            } else if (opp.marketType === 'spread') {
                // For spread: if opportunity is on Away, recommend Home spread (and vice versa)
                if (opp.side === 'Away') {
                    const homeSpread = market.home_spread;
                    const homeTeam = this.formatTeamName(opp.game.home_team);
                    return `Recommended Bet: ${homeTeam} ${homeSpread} ${this.formatOdds(market.home_odds)}`;
                } else {
                    const awaySpread = market.away_spread;
                    const awayTeam = this.formatTeamName(opp.game.away_team);
                    return `Recommended Bet: ${awayTeam} ${awaySpread} ${this.formatOdds(market.away_odds)}`;
                }
            } else {
                // For moneyline: if opportunity is on Away, recommend Home ML (and vice versa)
                if (opp.side === 'Away') {
                    const homeTeam = this.formatTeamName(opp.game.home_team);
                    return `Recommended Bet: ${homeTeam} ML ${this.formatOdds(market.home_odds)}`;
                } else {
                    const awayTeam = this.formatTeamName(opp.game.away_team);
                    return `Recommended Bet: ${awayTeam} ML ${this.formatOdds(market.away_odds)}`;
                }
            }
        }

        // For all other opportunity types (contrarian-prime, sharp-divergence, etc.),
        // show the complete bet recommendation for the identified side
        if (opp.marketType === 'totals') {
            const market = opp.game[opp.marketType];
            const recommendedOdds = opp.recommendedSide === 'Over' ? market.over_odds : market.under_odds;
            return `Recommended Bet: ${opp.recommendedSide} ${opp.spread || 'TBD'} ${this.formatOdds(recommendedOdds)}`;
        } else if (opp.marketType === 'spread') {
            const market = opp.game[opp.marketType];
            const teamName = opp.recommendedSide === 'Away' ?
                this.formatTeamName(opp.game.away_team) :
                this.formatTeamName(opp.game.home_team);
            const recommendedSpread = opp.recommendedSide === 'Away' ? market.away_spread : market.home_spread;
            const recommendedOdds = opp.recommendedSide === 'Away' ? market.away_odds : market.home_odds;
            return `Recommended Bet: ${teamName} ${recommendedSpread} ${this.formatOdds(recommendedOdds)}`;
        } else {
            // Moneyline - use stored recommendedSide from opportunity calculation
            const teamName = opp.recommendedSide === 'Away' ?
                this.formatTeamName(opp.game.away_team) :
                this.formatTeamName(opp.game.home_team);
            const market = opp.game[opp.marketType];
            const recommendedOdds = opp.recommendedSide === 'Away' ? market.away_odds : market.home_odds;
            return `Recommended Bet: ${teamName} ML ${this.formatOdds(recommendedOdds)}`;
        }
    }

    // Carousel Methods
    initializeCarousels() {
        console.log('[Carousel] Initializing carousels on mobile...');
        const carouselWrappers = document.querySelectorAll('.market-carousel-wrapper');

        carouselWrappers.forEach(wrapper => {
            const carousel = wrapper.querySelector('.markets-analysis.carousel');
            const pagination = wrapper.querySelector('.carousel-pagination');

            if (!carousel || !pagination) return;

            // Set up scroll event listener with throttling
            let scrollTimeout;
            carousel.addEventListener('scroll', () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    this.updateCarouselDots(carousel, pagination);
                }, 50);
            });

            // Set up dot click handlers
            const dots = pagination.querySelectorAll('.dot');
            dots.forEach(dot => {
                dot.addEventListener('click', () => {
                    const index = parseInt(dot.dataset.index);
                    this.scrollToMarket(carousel, index);
                });
            });

            console.log('[Carousel] Initialized carousel with', dots.length, 'markets');
        });
    }

    updateCarouselDots(carousel, pagination) {
        const markets = carousel.querySelectorAll('.market-analysis');
        const dots = pagination.querySelectorAll('.dot');

        if (markets.length === 0 || dots.length === 0) return;

        // Calculate which market is most visible
        const scrollLeft = carousel.scrollLeft;
        const carouselWidth = carousel.clientWidth;
        const marketWidth = markets[0].offsetWidth + parseFloat(getComputedStyle(carousel).gap || 0);

        // Determine active index based on scroll position
        const activeIndex = Math.round(scrollLeft / marketWidth);

        // Update dot active states
        dots.forEach((dot, index) => {
            if (index === activeIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    scrollToMarket(carousel, index) {
        const markets = carousel.querySelectorAll('.market-analysis');
        if (index >= 0 && index < markets.length) {
            const targetMarket = markets[index];
            targetMarket.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'start'
            });
        }
    }

    initializeOpportunitiesCarousel() {
        console.log('[Carousel] Initializing opportunities carousel on mobile...');
        const wrapper = document.querySelector('.opportunities-carousel-wrapper');

        if (!wrapper) {
            console.log('[Carousel] No opportunities carousel wrapper found');
            return;
        }

        const carousel = wrapper.querySelector('.opportunities-list.carousel');
        const pagination = wrapper.querySelector('.carousel-pagination');

        if (!carousel || !pagination) {
            console.log('[Carousel] Missing carousel or pagination elements');
            return;
        }

        // Set up scroll event listener with throttling
        let scrollTimeout;
        carousel.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.updateOpportunityCarouselDots(carousel, pagination);
            }, 50);
        });

        // Set up dot click handlers
        const dots = pagination.querySelectorAll('.dot');
        dots.forEach(dot => {
            dot.addEventListener('click', () => {
                const index = parseInt(dot.dataset.index);
                this.scrollToOpportunity(carousel, index);
            });
        });

        console.log('[Carousel] Initialized opportunities carousel with', dots.length, 'opportunities');
    }

    updateOpportunityCarouselDots(carousel, pagination) {
        const opportunities = carousel.querySelectorAll('.opportunity-item');
        const dots = pagination.querySelectorAll('.dot');

        if (opportunities.length === 0 || dots.length === 0) return;

        // Calculate which opportunity is most visible
        const scrollLeft = carousel.scrollLeft;
        const carouselWidth = carousel.clientWidth;
        const opportunityWidth = opportunities[0].offsetWidth + parseFloat(getComputedStyle(carousel).gap || 0);

        // Determine active index based on scroll position
        const activeIndex = Math.round(scrollLeft / opportunityWidth);

        // Update dot active states
        dots.forEach((dot, index) => {
            if (index === activeIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    scrollToOpportunity(carousel, index) {
        const opportunities = carousel.querySelectorAll('.opportunity-item');
        if (index >= 0 && index < opportunities.length) {
            const targetOpportunity = opportunities[index];
            targetOpportunity.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'start'
            });
        }
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, checking for NFL page elements...');

    // Check if this is the NFL page (has required elements)
    const isNFLPage = document.getElementById('refreshBtn') !== null;

    if (isNFLPage) {
        console.log('NFL page detected, initializing full NFL Betting App...');

        // Check if CSS loaded
        const cssLoaded = document.styleSheets.length > 0;
        console.log(`CSS loaded: ${cssLoaded} (${document.styleSheets.length} stylesheets)`);

        // Initialize full app
        window.nflApp = new NFLBettingApp();
    } else {
        console.log('Not NFL page, creating lightweight NFL app for calculations only...');

        // Create a lightweight object with just the calculation methods
        // All methods need to be bound to the same context object
        const context = {};
        context.calculateGameOpportunities = NFLBettingApp.prototype.calculateGameOpportunities.bind(context);
        context.calculateOpportunityScore = NFLBettingApp.prototype.calculateOpportunityScore.bind(context);
        context.getTeamOrSide = NFLBettingApp.prototype.getTeamOrSide.bind(context);
        context.getOppositeSide = NFLBettingApp.prototype.getOppositeSide.bind(context);
        context.formatTeamName = NFLBettingApp.prototype.formatTeamName.bind(context);
        context.parseAmericanOdds = NFLBettingApp.prototype.parseAmericanOdds.bind(context);
        context.findTopOpportunities = NFLBettingApp.prototype.findTopOpportunities.bind(context);

        window.nflApp = context;
    }
    
    // Add a fallback test
    setTimeout(() => {
        const header = document.querySelector('header');
        if (header) {
            const styles = window.getComputedStyle(header);
            console.log('Header background:', styles.background);
            if (styles.background === 'rgba(0, 0, 0, 0) none repeat scroll 0% 0% / auto padding-box border-box') {
                console.warn('CSS may not be loading - header has no background');
            }
        }
    }, 1000);
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.nflApp) {
        window.nflApp.stopAutoRefresh();
    }
});