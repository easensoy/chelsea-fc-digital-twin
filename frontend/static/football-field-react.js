// React-based Football Field Component
// Note: This requires React and React DOM to be loaded

const { useState, useEffect, useRef } = React;

const FootballFieldReact = ({
    width = 800,
    height = 520,
    interactive = true,
    showPlayerPositions = false,
    formation = '4-3-3',
    players = [],
    heatmapData = [],
    onPlayerClick = null,
    onFieldClick = null,
    showHeatmap = false,
    theme = 'standard'
}) => {
    const svgRef = useRef(null);
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [hoveredArea, setHoveredArea] = useState(null);

    const themes = {
        standard: {
            grass: '#2d8f31',
            grassStripes: ['#2d8f31', '#259d2b'],
            lines: 'white',
            playerHome: '#3d85c6',
            playerAway: '#dc3545',
            goalkeeper: '#1f4e79'
        },
        night: {
            grass: '#1a4a1e',
            grassStripes: ['#1a4a1e', '#1e5722'],
            lines: '#f0f0f0',
            playerHome: '#4dabf7',
            playerAway: '#ff6b6b',
            goalkeeper: '#228be6'
        },
        vintage: {
            grass: '#3e6b41',
            grassStripes: ['#3e6b41', '#4a7d4e'],
            lines: '#f5f5dc',
            playerHome: '#8b4513',
            playerAway: '#800080',
            goalkeeper: '#556b2f'
        }
    };

    const currentTheme = themes[theme] || themes.standard;

    const formations = {
        '4-3-3': [
            { x: 0.08, y: 0.5, position: 'GK', number: 1 },
            { x: 0.25, y: 0.2, position: 'RB', number: 2 },
            { x: 0.25, y: 0.4, position: 'CB', number: 5 },
            { x: 0.25, y: 0.6, position: 'CB', number: 6 },
            { x: 0.25, y: 0.8, position: 'LB', number: 3 },
            { x: 0.5, y: 0.3, position: 'CM', number: 8 },
            { x: 0.5, y: 0.5, position: 'CM', number: 4 },
            { x: 0.5, y: 0.7, position: 'CM', number: 10 },
            { x: 0.75, y: 0.25, position: 'RW', number: 7 },
            { x: 0.75, y: 0.5, position: 'ST', number: 9 },
            { x: 0.75, y: 0.75, position: 'LW', number: 11 }
        ],
        '4-4-2': [
            { x: 0.08, y: 0.5, position: 'GK', number: 1 },
            { x: 0.25, y: 0.2, position: 'RB', number: 2 },
            { x: 0.25, y: 0.4, position: 'CB', number: 5 },
            { x: 0.25, y: 0.6, position: 'CB', number: 6 },
            { x: 0.25, y: 0.8, position: 'LB', number: 3 },
            { x: 0.5, y: 0.25, position: 'RM', number: 7 },
            { x: 0.5, y: 0.42, position: 'CM', number: 8 },
            { x: 0.5, y: 0.58, position: 'CM', number: 4 },
            { x: 0.5, y: 0.75, position: 'LM', number: 11 },
            { x: 0.75, y: 0.4, position: 'ST', number: 9 },
            { x: 0.75, y: 0.6, position: 'ST', number: 10 }
        ]
    };

    const handlePlayerClick = (player, event) => {
        event.stopPropagation();
        setSelectedPlayer(player);
        if (onPlayerClick) {
            onPlayerClick(player);
        }
    };

    const handleFieldClick = (event) => {
        const rect = svgRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        setSelectedPlayer(null);
        if (onFieldClick) {
            onFieldClick(x, y);
        }
    };

    const GrassPattern = () => {
        const stripes = 12;
        const stripeHeight = (height - 20) / stripes;

        return (
            <>
                {Array.from({ length: stripes }, (_, i) => (
                    <rect
                        key={i}
                        x={10}
                        y={10 + (i * stripeHeight)}
                        width={width - 20}
                        height={stripeHeight}
                        fill={currentTheme.grassStripes[i % 2]}
                    />
                ))}
            </>
        );
    };

    const FieldMarkings = () => (
        <>
            {/* Outer boundary */}
            <rect x={10} y={10} width={width - 20} height={height - 20}
                  fill="none" stroke={currentTheme.lines} strokeWidth={3} />

            {/* Center line */}
            <line x1={width / 2} y1={10} x2={width / 2} y2={height - 10}
                  stroke={currentTheme.lines} strokeWidth={3} />

            {/* Center circle */}
            <circle cx={width / 2} cy={height / 2} r={60}
                    fill="none" stroke={currentTheme.lines} strokeWidth={3} />

            {/* Center spot */}
            <circle cx={width / 2} cy={height / 2} r={3} fill={currentTheme.lines} />

            {/* Left penalty area */}
            <rect x={10} y={height / 2 - 110} width={110} height={220}
                  fill="none" stroke={currentTheme.lines} strokeWidth={3} />

            {/* Right penalty area */}
            <rect x={width - 120} y={height / 2 - 110} width={110} height={220}
                  fill="none" stroke={currentTheme.lines} strokeWidth={3} />

            {/* Left 6-yard box */}
            <rect x={10} y={height / 2 - 40} width={40} height={80}
                  fill="none" stroke={currentTheme.lines} strokeWidth={3} />

            {/* Right 6-yard box */}
            <rect x={width - 50} y={height / 2 - 40} width={40} height={80}
                  fill="none" stroke={currentTheme.lines} strokeWidth={3} />

            {/* Penalty spots */}
            <circle cx={75} cy={height / 2} r={3} fill={currentTheme.lines} />
            <circle cx={width - 75} cy={height / 2} r={3} fill={currentTheme.lines} />

            {/* Goals */}
            <rect x={-5} y={height / 2 - 15} width={15} height={30}
                  fill="none" stroke={currentTheme.lines} strokeWidth={2} />
            <rect x={width - 10} y={height / 2 - 15} width={15} height={30}
                  fill="none" stroke={currentTheme.lines} strokeWidth={2} />

            {/* Corner arcs */}
            <path d={`M 18 10 A 8 8 0 0 0 10 18`}
                  fill="none" stroke={currentTheme.lines} strokeWidth={2} />
            <path d={`M ${width - 18} 10 A 8 8 0 0 1 ${width - 10} 18`}
                  fill="none" stroke={currentTheme.lines} strokeWidth={2} />
            <path d={`M 18 ${height - 10} A 8 8 0 0 1 10 ${height - 18}`}
                  fill="none" stroke={currentTheme.lines} strokeWidth={2} />
            <path d={`M ${width - 18} ${height - 10} A 8 8 0 0 0 ${width - 10} ${height - 18}`}
                  fill="none" stroke={currentTheme.lines} strokeWidth={2} />

            {/* Corner flags */}
            <line x1={10} y1={10} x2={10} y2={-5} stroke="#ffd700" strokeWidth={2} />
            <rect x={10} y={-5} width={8} height={6} fill="#ff4444" />

            <line x1={width - 10} y1={10} x2={width - 10} y2={-5} stroke="#ffd700" strokeWidth={2} />
            <rect x={width - 18} y={-5} width={8} height={6} fill="#ff4444" />

            <line x1={10} y1={height - 10} x2={10} y2={height + 5} stroke="#ffd700" strokeWidth={2} />
            <rect x={10} y={height - 1} width={8} height={6} fill="#ff4444" />

            <line x1={width - 10} y1={height - 10} x2={width - 10} y2={height + 5} stroke="#ffd700" strokeWidth={2} />
            <rect x={width - 18} y={height - 1} width={8} height={6} fill="#ff4444" />
        </>
    );

    const PlayerPositions = () => {
        const positions = formations[formation] || formations['4-3-3'];
        const playersToRender = players.length > 0 ? players : positions;

        return (
            <g className="player-positions">
                {playersToRender.map((player, index) => {
                    const x = player.x * width;
                    const y = player.y * height;
                    const isSelected = selectedPlayer && selectedPlayer.number === player.number;
                    const isGoalkeeper = player.position === 'GK' || index === 0;

                    return (
                        <g key={player.number || index} className="player">
                            {/* Player circle */}
                            <circle
                                cx={x}
                                cy={y}
                                r={isSelected ? 15 : 12}
                                fill={isGoalkeeper ? currentTheme.goalkeeper : currentTheme.playerHome}
                                stroke={isSelected ? '#fff' : currentTheme.lines}
                                strokeWidth={isSelected ? 3 : 2}
                                style={{ cursor: interactive ? 'pointer' : 'default' }}
                                onClick={interactive ? (e) => handlePlayerClick(player, e) : undefined}
                                className={`player-circle ${isSelected ? 'selected' : ''}`}
                            />

                            {/* Player number */}
                            <text
                                x={x}
                                y={y + 4}
                                fill="white"
                                fontSize="12"
                                fontFamily="Arial, sans-serif"
                                textAnchor="middle"
                                fontWeight="bold"
                                style={{ pointerEvents: 'none' }}
                            >
                                {player.number || index + 1}
                            </text>

                            {/* Player name (if selected) */}
                            {isSelected && player.name && (
                                <text
                                    x={x}
                                    y={y - 25}
                                    fill={currentTheme.lines}
                                    fontSize="10"
                                    fontFamily="Arial, sans-serif"
                                    textAnchor="middle"
                                    fontWeight="bold"
                                    style={{ pointerEvents: 'none' }}
                                >
                                    {player.name}
                                </text>
                            )}
                        </g>
                    );
                })}
            </g>
        );
    };

    const Heatmap = () => {
        if (!showHeatmap || !heatmapData.length) return null;

        const maxValue = Math.max(...heatmapData.map(d => d.value));

        return (
            <g className="heatmap">
                {heatmapData.map((data, index) => {
                    const intensity = data.value / maxValue;
                    return (
                        <circle
                            key={index}
                            cx={data.x}
                            cy={data.y}
                            r={25}
                            fill={`rgba(255, 0, 0, ${intensity * 0.6})`}
                            style={{ pointerEvents: 'none' }}
                        />
                    );
                })}
            </g>
        );
    };

    return (
        <div className="football-field-container" style={{ position: 'relative' }}>
            <svg
                ref={svgRef}
                width={width}
                height={height}
                viewBox={`0 0 ${width} ${height}`}
                style={{
                    background: currentTheme.grass,
                    border: '2px solid #1a5c1e',
                    borderRadius: '8px',
                    cursor: interactive ? 'pointer' : 'default'
                }}
                onClick={interactive ? handleFieldClick : undefined}
            >
                <GrassPattern />
                <FieldMarkings />
                {showHeatmap && <Heatmap />}
                {showPlayerPositions && <PlayerPositions />}
            </svg>

            {/* Player info panel */}
            {selectedPlayer && (
                <div
                    style={{
                        position: 'absolute',
                        top: '10px',
                        right: '10px',
                        background: 'rgba(255, 255, 255, 0.95)',
                        border: '1px solid #ccc',
                        borderRadius: '8px',
                        padding: '10px',
                        fontSize: '14px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                >
                    <h4 style={{ margin: '0 0 8px 0' }}>
                        {selectedPlayer.name || `Player ${selectedPlayer.number}`}
                    </h4>
                    <p style={{ margin: '4px 0' }}>
                        <strong>Position:</strong> {selectedPlayer.position}
                    </p>
                    <p style={{ margin: '4px 0' }}>
                        <strong>Number:</strong> {selectedPlayer.number}
                    </p>
                    {selectedPlayer.rating && (
                        <p style={{ margin: '4px 0' }}>
                            <strong>Rating:</strong> {selectedPlayer.rating}
                        </p>
                    )}
                </div>
            )}
        </div>
    );
};

// Formation Selector Component
const FormationSelector = ({ currentFormation, onFormationChange, formations = ['4-3-3', '4-4-2', '3-5-2', '4-2-3-1'] }) => {
    return (
        <div className="formation-selector" style={{ margin: '10px 0' }}>
            <label style={{ marginRight: '10px', fontWeight: 'bold' }}>Formation:</label>
            <select
                value={currentFormation}
                onChange={(e) => onFormationChange(e.target.value)}
                style={{
                    padding: '5px 10px',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    fontSize: '14px'
                }}
            >
                {formations.map(formation => (
                    <option key={formation} value={formation}>
                        {formation}
                    </option>
                ))}
            </select>
        </div>
    );
};

// Complete Field Application Component
const FootballFieldApp = () => {
    const [formation, setFormation] = useState('4-3-3');
    const [showHeatmap, setShowHeatmap] = useState(false);
    const [theme, setTheme] = useState('standard');
    const [players, setPlayers] = useState([]);

    const handlePlayerClick = (player) => {
        console.log('Player clicked:', player);
    };

    const handleFieldClick = (x, y) => {
        console.log('Field clicked at:', x, y);
    };

    const sampleHeatmapData = [
        { x: 200, y: 200, value: 0.8 },
        { x: 300, y: 150, value: 0.6 },
        { x: 400, y: 260, value: 1.0 },
        { x: 500, y: 200, value: 0.4 }
    ];

    return (
        <div>
            <div style={{ marginBottom: '20px' }}>
                <FormationSelector
                    currentFormation={formation}
                    onFormationChange={setFormation}
                />

                <label style={{ marginRight: '10px' }}>
                    <input
                        type="checkbox"
                        checked={showHeatmap}
                        onChange={(e) => setShowHeatmap(e.target.checked)}
                    />
                    Show Heatmap
                </label>

                <label style={{ marginLeft: '20px', marginRight: '10px' }}>Theme:</label>
                <select
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                    style={{
                        padding: '5px 10px',
                        border: '1px solid #ccc',
                        borderRadius: '4px'
                    }}
                >
                    <option value="standard">Standard</option>
                    <option value="night">Night</option>
                    <option value="vintage">Vintage</option>
                </select>
            </div>

            <FootballFieldReact
                width={800}
                height={520}
                formation={formation}
                showPlayerPositions={true}
                interactive={true}
                onPlayerClick={handlePlayerClick}
                onFieldClick={handleFieldClick}
                showHeatmap={showHeatmap}
                heatmapData={showHeatmap ? sampleHeatmapData : []}
                theme={theme}
            />
        </div>
    );
};

// Export components
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        FootballFieldReact,
        FormationSelector,
        FootballFieldApp
    };
}