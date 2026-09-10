with sc1_right:
        st.markdown(f"<div class='blue-card'><div class='blue-card-title'>INCOME TREND ({selected_q})</div>", unsafe_allow_html=True)
        fig_trend = go.Figure()
        # Only the Total Income line is added here now
        fig_trend.add_trace(go.Scatter(
            x=q_ctx['months'], 
            y=q_ctx['income_trend'], 
            name='Total Income', 
            line=dict(color=BLUE_ACCENT, width=2.5, shape='spline', smoothing=0.3), 
            mode='lines+markers', 
            marker=dict(size=8)
        ))
        
        fig_trend.update_layout(
            margin=dict(t=20, b=20, l=10, r=10), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            # Legend is hidden since there is only one line now
            showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=13), range=[-0.8, 2.8]), 
            yaxis=dict(
                showgrid=True, gridcolor='#E2E8F0', 
                tickfont=dict(color="#0F172A", size=13), 
                zeroline=False,
                tickformat="d",
                ticksuffix=" PKR Mns"
            ), 
            height=270, 
            font=CHART_FONT
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
