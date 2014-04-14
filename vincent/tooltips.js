vg_mouseover = function(x, y, x_pos, y_pos){
                // Clean up lost tooltips
                d3.select('body').selectAll('div.tooltip').remove();
                // Append tooltip
                tooltipDiv = d3.select('body')
                               .append('div')
                               .attr('class', 'tooltip');
                tooltipDiv.style({
                    left: (x_pos + 10)+'px',
                    top: (y_pos - 40)+'px',
                    'background-color': '#d8d5e4',
                    width: '50px',
                    height: '40px',
                    padding: '5px',
                    position: 'absolute',
                    opacity: 0.7,
                    'z-index': 1001,
                    'box-shadow': '0 1px 2px 0 #656565'
                });

                var first_line = '<p>X: ' + x + '</p>';
                var second_line = '<p>Y: ' + y + '</p>';

                tooltipDiv.html(first_line + second_line);
            };

vg_mousemove = function(x, y, x_pos, y_pos){
                // Move tooltip
                tooltipDiv.style({
                    left: (x_pos + 10)+'px',
                    top: (y_pos - 40)+'px'
                });
            };

vg_mouseout = function(x, y){
                // Remove tooltip
                tooltipDiv.remove();
            };

