class FootballField {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 800,
            height: options.height || 520,
            interactive: options.interactive || false,
            showPlayerPositions: options.showPlayerPositions || false,
            formation: options.formation || '4-3-3',
            ...options
        };

        this.fieldWidth = this.options.width;
        this.fieldHeight = this.options.height;

        this.init();
    }

    init() {
        this.createSVG();
        this.drawField();

        if (this.options.interactive) {
            this.makeInteractive();
        }

        if (this.options.showPlayerPositions) {
            this.drawPlayerPositions();
        }
    }

    createSVG() {
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', this.fieldWidth);
        this.svg.setAttribute('height', this.fieldHeight);
        this.svg.setAttribute('viewBox', `0 0 ${this.fieldWidth} ${this.fieldHeight}`);
        this.svg.style.background = '#2d8f31';
        this.svg.style.border = '2px solid #1a5c1e';
        this.svg.style.borderRadius = '8px';

        this.container.appendChild(this.svg);
    }

    drawField() {
        // Field grass pattern
        this.drawGrassPattern();

        // Outer boundary
        this.drawRect(10, 10, this.fieldWidth - 20, this.fieldHeight - 20, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 3
        });

        // Center line
        this.drawLine(this.fieldWidth / 2, 10, this.fieldWidth / 2, this.fieldHeight - 10, {
            stroke: 'white',
            strokeWidth: 3
        });

        // Center circle
        this.drawCircle(this.fieldWidth / 2, this.fieldHeight / 2, 60, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 3
        });

        // Center spot
        this.drawCircle(this.fieldWidth / 2, this.fieldHeight / 2, 3, {
            fill: 'white'
        });

        // Left penalty area
        this.drawRect(10, this.fieldHeight / 2 - 110, 110, 220, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 3
        });

        // Right penalty area
        this.drawRect(this.fieldWidth - 120, this.fieldHeight / 2 - 110, 110, 220, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 3
        });

        // Left 6-yard box
        this.drawRect(10, this.fieldHeight / 2 - 40, 40, 80, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 3
        });

        // Right 6-yard box
        this.drawRect(this.fieldWidth - 50, this.fieldHeight / 2 - 40, 40, 80, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 3
        });

        // Left penalty spot
        this.drawCircle(75, this.fieldHeight / 2, 3, {
            fill: 'white'
        });

        // Right penalty spot
        this.drawCircle(this.fieldWidth - 75, this.fieldHeight / 2, 3, {
            fill: 'white'
        });

        // Left penalty arc
        this.drawArc(75, this.fieldHeight / 2, 60, 140, 220, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 3
        });

        // Right penalty arc
        this.drawArc(this.fieldWidth - 75, this.fieldHeight / 2, 60, 320, 40, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 3
        });

        // Goals
        this.drawGoal(10, this.fieldHeight / 2 - 15, 'left');
        this.drawGoal(this.fieldWidth - 10, this.fieldHeight / 2 - 15, 'right');

        // Corner arcs
        this.drawCornerArc(10, 10, 'top-left');
        this.drawCornerArc(this.fieldWidth - 10, 10, 'top-right');
        this.drawCornerArc(10, this.fieldHeight - 10, 'bottom-left');
        this.drawCornerArc(this.fieldWidth - 10, this.fieldHeight - 10, 'bottom-right');

        // Corner flags
        this.drawCornerFlag(10, 10);
        this.drawCornerFlag(this.fieldWidth - 10, 10);
        this.drawCornerFlag(10, this.fieldHeight - 10);
        this.drawCornerFlag(this.fieldWidth - 10, this.fieldHeight - 10);
    }

    drawGrassPattern() {
        const stripes = 12;
        const stripeHeight = (this.fieldHeight - 20) / stripes;

        for (let i = 0; i < stripes; i++) {
            const color = i % 2 === 0 ? '#2d8f31' : '#259d2b';
            this.drawRect(10, 10 + (i * stripeHeight), this.fieldWidth - 20, stripeHeight, {
                fill: color,
                stroke: 'none'
            });
        }
    }

    drawGoal(x, y, side) {
        const goalWidth = 30;
        const goalHeight = 20;

        if (side === 'left') {
            // Left goal
            this.drawRect(x - 15, y, 15, goalHeight, {
                fill: 'none',
                stroke: 'white',
                strokeWidth: 2
            });
            // Goal net pattern
            for (let i = 0; i < 3; i++) {
                this.drawLine(x - 15 + (i * 5), y, x - 15 + (i * 5), y + goalHeight, {
                    stroke: 'white',
                    strokeWidth: 0.5,
                    opacity: 0.6
                });
            }
        } else {
            // Right goal
            this.drawRect(x, y, 15, goalHeight, {
                fill: 'none',
                stroke: 'white',
                strokeWidth: 2
            });
            // Goal net pattern
            for (let i = 0; i < 3; i++) {
                this.drawLine(x + (i * 5), y, x + (i * 5), y + goalHeight, {
                    stroke: 'white',
                    strokeWidth: 0.5,
                    opacity: 0.6
                });
            }
        }
    }

    drawCornerArc(x, y, corner) {
        const radius = 8;
        let startAngle, endAngle;

        switch (corner) {
            case 'top-left':
                startAngle = 270;
                endAngle = 360;
                break;
            case 'top-right':
                startAngle = 180;
                endAngle = 270;
                break;
            case 'bottom-left':
                startAngle = 0;
                endAngle = 90;
                break;
            case 'bottom-right':
                startAngle = 90;
                endAngle = 180;
                break;
        }

        this.drawArc(x, y, radius, startAngle, endAngle, {
            fill: 'none',
            stroke: 'white',
            strokeWidth: 2
        });
    }

    drawCornerFlag(x, y) {
        // Flag pole
        this.drawLine(x, y, x, y - 15, {
            stroke: '#ffd700',
            strokeWidth: 2
        });

        // Flag
        this.drawRect(x, y - 15, 8, 6, {
            fill: '#ff4444',
            stroke: 'none'
        });
    }

    drawPlayerPositions() {
        const formations = {
            '4-3-3': [
                // GK
                { x: 0.08, y: 0.5 },
                // Defense
                { x: 0.25, y: 0.2 }, { x: 0.25, y: 0.4 }, { x: 0.25, y: 0.6 }, { x: 0.25, y: 0.8 },
                // Midfield
                { x: 0.5, y: 0.3 }, { x: 0.5, y: 0.5 }, { x: 0.5, y: 0.7 },
                // Attack
                { x: 0.75, y: 0.25 }, { x: 0.75, y: 0.5 }, { x: 0.75, y: 0.75 }
            ],
            '4-4-2': [
                // GK
                { x: 0.08, y: 0.5 },
                // Defense
                { x: 0.25, y: 0.2 }, { x: 0.25, y: 0.4 }, { x: 0.25, y: 0.6 }, { x: 0.25, y: 0.8 },
                // Midfield
                { x: 0.5, y: 0.25 }, { x: 0.5, y: 0.42 }, { x: 0.5, y: 0.58 }, { x: 0.5, y: 0.75 },
                // Attack
                { x: 0.75, y: 0.4 }, { x: 0.75, y: 0.6 }
            ]
        };

        const positions = formations[this.options.formation] || formations['4-3-3'];

        positions.forEach((pos, index) => {
            const x = pos.x * this.fieldWidth;
            const y = pos.y * this.fieldHeight;

            // Player circle
            this.drawCircle(x, y, 12, {
                fill: index === 0 ? '#1f4e79' : '#3d85c6',
                stroke: 'white',
                strokeWidth: 2
            });

            // Player number
            this.drawText(x, y + 2, index + 1, {
                fill: 'white',
                fontSize: '12px',
                fontFamily: 'Arial, sans-serif',
                textAnchor: 'middle',
                fontWeight: 'bold'
            });
        });
    }

    makeInteractive() {
        this.svg.style.cursor = 'pointer';

        this.svg.addEventListener('click', (e) => {
            const rect = this.svg.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            this.onFieldClick(x, y);
        });

        this.svg.addEventListener('mousemove', (e) => {
            const rect = this.svg.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            this.onFieldHover(x, y);
        });
    }

    onFieldClick(x, y) {
        // Override this method for custom click handling
        console.log(`Field clicked at: ${x}, ${y}`);

        if (this.options.onFieldClick) {
            this.options.onFieldClick(x, y);
        }
    }

    onFieldHover(x, y) {
        // Override this method for custom hover handling
        if (this.options.onFieldHover) {
            this.options.onFieldHover(x, y);
        }
    }

    addHeatmapData(heatmapData) {
        // Add heatmap visualization
        const maxValue = Math.max(...heatmapData.map(d => d.value));

        heatmapData.forEach(data => {
            const intensity = data.value / maxValue;
            const radius = 25;

            this.drawCircle(data.x, data.y, radius, {
                fill: `rgba(255, 0, 0, ${intensity * 0.6})`,
                stroke: 'none'
            });
        });
    }

    highlightArea(x, y, width, height, color = 'rgba(255, 255, 0, 0.3)') {
        this.drawRect(x, y, width, height, {
            fill: color,
            stroke: 'none'
        });
    }

    // Helper drawing methods
    drawRect(x, y, width, height, styles = {}) {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', x);
        rect.setAttribute('y', y);
        rect.setAttribute('width', width);
        rect.setAttribute('height', height);

        this.applyStyles(rect, styles);
        this.svg.appendChild(rect);
        return rect;
    }

    drawCircle(cx, cy, r, styles = {}) {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('r', r);

        this.applyStyles(circle, styles);
        this.svg.appendChild(circle);
        return circle;
    }

    drawLine(x1, y1, x2, y2, styles = {}) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);

        this.applyStyles(line, styles);
        this.svg.appendChild(line);
        return line;
    }

    drawArc(cx, cy, r, startAngle, endAngle, styles = {}) {
        const startRadians = (startAngle * Math.PI) / 180;
        const endRadians = (endAngle * Math.PI) / 180;

        const x1 = cx + r * Math.cos(startRadians);
        const y1 = cy + r * Math.sin(startRadians);
        const x2 = cx + r * Math.cos(endRadians);
        const y2 = cy + r * Math.sin(endRadians);

        const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const d = `M ${x1} ${y1} A ${r} ${r} 0 ${largeArcFlag} 1 ${x2} ${y2}`;
        path.setAttribute('d', d);

        this.applyStyles(path, styles);
        this.svg.appendChild(path);
        return path;
    }

    drawText(x, y, text, styles = {}) {
        const textElement = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textElement.setAttribute('x', x);
        textElement.setAttribute('y', y);
        textElement.textContent = text;

        this.applyStyles(textElement, styles);
        this.svg.appendChild(textElement);
        return textElement;
    }

    applyStyles(element, styles) {
        Object.keys(styles).forEach(key => {
            if (key === 'strokeWidth') {
                element.setAttribute('stroke-width', styles[key]);
            } else if (key === 'textAnchor') {
                element.setAttribute('text-anchor', styles[key]);
            } else if (key === 'fontFamily') {
                element.setAttribute('font-family', styles[key]);
            } else if (key === 'fontSize') {
                element.setAttribute('font-size', styles[key]);
            } else if (key === 'fontWeight') {
                element.setAttribute('font-weight', styles[key]);
            } else {
                element.setAttribute(key, styles[key]);
            }
        });
    }

    clear() {
        while (this.svg.firstChild) {
            this.svg.removeChild(this.svg.firstChild);
        }
    }

    redraw() {
        this.clear();
        this.drawField();

        if (this.options.showPlayerPositions) {
            this.drawPlayerPositions();
        }
    }

    updateFormation(formation) {
        this.options.formation = formation;
        if (this.options.showPlayerPositions) {
            this.redraw();
        }
    }

    exportAsSVG() {
        return this.svg.outerHTML;
    }

    exportAsPNG(callback) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();

        canvas.width = this.fieldWidth;
        canvas.height = this.fieldHeight;

        const svgData = new XMLSerializer().serializeToString(this.svg);
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
        const svgUrl = URL.createObjectURL(svgBlob);

        img.onload = function() {
            ctx.drawImage(img, 0, 0);
            URL.revokeObjectURL(svgUrl);

            canvas.toBlob(callback, 'image/png');
        };

        img.src = svgUrl;
    }
}

// Usage examples and factory functions
const FootballFieldFactory = {
    createStandardField: (containerId, options = {}) => {
        return new FootballField(containerId, {
            width: 800,
            height: 520,
            interactive: false,
            ...options
        });
    },

    createInteractiveField: (containerId, options = {}) => {
        return new FootballField(containerId, {
            width: 800,
            height: 520,
            interactive: true,
            showPlayerPositions: true,
            ...options
        });
    },

    createFormationBoard: (containerId, formation = '4-3-3', options = {}) => {
        return new FootballField(containerId, {
            width: 600,
            height: 400,
            interactive: true,
            showPlayerPositions: true,
            formation: formation,
            ...options
        });
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FootballField, FootballFieldFactory };
}