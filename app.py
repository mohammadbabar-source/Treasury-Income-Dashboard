# Screen 1 Charts 
    sc1_left, sc1_right = st.columns([1, 1.8], gap="medium")

    with sc1_left:
        st.markdown(f"<div class='blue-card'><div class='blue-card-title'>INCOME MARGIN DISTRIBUTION ({selected_q})</div>", unsafe_allow_html=True)
        fig_margin = go.Figure(data=[go.Pie(
            labels=q_ctx['margin_labels'], 
            values=q_ctx['margin_values'], hole=0.68,
            marker_colors=[BLUE_ACCENT, '#60A5FA', GREEN_ACCENT, '#93C5FD'], 
            textinfo='label+percent', 
            textposition='outside', 
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_margin.update_layout(
            annotations=[dict(text=f"Total<br><b style='font-size:20px; color:#0F172A;'>{q_ctx['total_income']:.1f}M</b>", x=0.5, y=0.5, xanchor='center', yanchor='middle', font=CHART_FONT, showarrow=False)],
            showlegend=False, 
            margin=dict(t=10, b=10, l=30, r=30), # Tighter margins
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=220, # Ultra-compact height
            font=CHART_FONT
        )
        st.plotly_chart(fig_margin, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with sc1_right:
        st.markdown(f"<div class='blue-card'><div class='blue-card-title'>INCOME TREND ({selected_q})</div>", unsafe_allow_html=True)
        fig_trend = go.Figure()
        # Even thinner line (width: 2) and smaller markers (size: 6)
        fig_trend.add_trace(go.Scatter(
            x=q_ctx['months'], 
            y=q_ctx['income_trend'], 
            name='Total Income', 
            line=dict(color=BLUE_ACCENT, width=2, shape='spline', smoothing=0.3), 
            mode='lines+markers', 
            marker=dict(size=6)
        ))
        fig_trend.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), # Removed all excess padding
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, 
            # Increased the range constraint from [-0.8, 2.8] to [-1.2, 3.2] to squeeze the line further to the center
            xaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=12), range=[-1.2, 3.2]), 
            yaxis=dict(
                showgrid=True, gridcolor='#E2E8F0', 
                tickfont=dict(color="#0F172A", size=12), 
                zeroline=False,
                tickformat="d",
                ticksuffix=" PKR Mns"
            ), 
            height=220, # Ultra-compact height
            font=CHART_FONT
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
