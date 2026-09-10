# Screen 1 Charts (Inside HTML Cards)
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
            annotations=[dict(text=f"Total<br><b style='font-size:22px; color:#0F172A;'>{q_ctx['total_income']:.1f}M</b>", x=0.5, y=0.5, xanchor='center', yanchor='middle', font=CHART_FONT, showarrow=False)],
            showlegend=False, 
            margin=dict(t=20, b=20, l=40, r=40), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=270, # Matched shorter height
            font=CHART_FONT
        )
        st.plotly_chart(fig_margin, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with sc1_right:
        st.markdown(f"<div class='blue-card'><div class='blue-card-title'>INCOME TREND ({selected_q})</div>", unsafe_allow_html=True)
        fig_trend = go.Figure()
        # Thinner lines (width 2.5) and slightly smaller markers
        fig_trend.add_trace(go.Scatter(x=q_ctx['months'], y=q_ctx['income_trend'], name='Total Income', line=dict(color=BLUE_ACCENT, width=2.5, shape='spline', smoothing=0.3), mode='lines+markers', marker=dict(size=8)))
        fig_trend.add_trace(go.Scatter(x=q_ctx['months'], y=q_ctx['expense_trend'], name='Total Expenses', line=dict(color=GREEN_ACCENT, width=2.5, shape='spline', smoothing=0.3), mode='lines+markers', marker=dict(size=8)))
        fig_trend.update_layout(
            margin=dict(t=20, b=20, l=10, r=10), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(yanchor="bottom", y=0.02, xanchor="right", x=0.98, font=dict(color="#0F172A", size=12)),
            # The range constraint forces the months closer together
            xaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=13), range=[-0.8, 2.8]), 
            yaxis=dict(
                showgrid=True, gridcolor='#E2E8F0', 
                tickfont=dict(color="#0F172A", size=13), 
                zeroline=False,
                tickformat="d",
                ticksuffix=" PKR Mns"
            ), 
            height=270, # Shorter overall chart height
            font=CHART_FONT
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
