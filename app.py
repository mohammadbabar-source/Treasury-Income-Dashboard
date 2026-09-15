# =========================================================
    # NEW SECTION: CURRENT INVESTMENT POSITION
    # =========================================================
    
    # 1. Spacer & Section Header
    st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: left; margin-bottom: 24px;">
            <h3 style="font-size: 25px; font-weight: 900; color: #0F172A; letter-spacing: 1.2px; text-transform: uppercase; margin: 0;">Current Investment Position</h3>
            <p style="color: #64748B; font-size: 16px; font-weight: 600; margin-top: 4px;">Instrument-Level Ledger & Portfolio Concentration</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Placeholder Data Structure (Ready for Excel/JSON mapping)
    # Using non-zero placeholder values so the chart renders properly during testing.
    investment_data = [
        {"instrument": "Savings Accounts", "value": 450.00, "conc": 45.0},
        {"instrument": "T-Bills", "value": 300.00, "conc": 30.0},
        {"instrument": "Buy/Sell", "value": 150.00, "conc": 15.0},
        {"instrument": "TDRs", "value": 100.00, "conc": 10.0}
    ]
    gross_portfolio_value = sum(item["value"] for item in investment_data)

    # 3. Two-Column Grid Setup (1fr : 1.4fr)
    inv_col1, inv_col2 = st.columns([1, 1.4], gap="large")

    # --- Left Card: Portfolio Concentration (Donut Chart) ---
    with inv_col1:
        # Wrap Plotly in a styled container
        st.markdown("""
            <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px 20px 0px 20px; box-shadow: 0 6px 16px rgba(30, 58, 138, 0.08);'>
                <div style='font-size: 18px; font-weight: 900; color: #0F172A; text-transform: uppercase;'>Portfolio Concentration</div>
                <div style='font-size: 13px; font-weight: 600; color: #64748B; margin-top: 4px;'>% of Gross Investment Portfolio</div>
            </div>
        """, unsafe_allow_html=True)
        
        fig_inv_donut = go.Figure(data=[go.Pie(
            labels=[item["instrument"] for item in investment_data],
            values=[item["value"] for item in investment_data],
            hole=0.65,
            marker_colors=['#2563EB', '#10B981', '#F59E0B', '#6366F1'],
            textinfo='label+percent',
            textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        
        fig_inv_donut.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=40, r=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=320,
            font=CHART_FONT
        )
        
        # Rendering chart with a negative top margin to pull it up seamlessly into the custom HTML card header above it
        st.markdown("<div style='margin-top: -15px; background: #FFFFFF; border-left: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; box-shadow: 0 6px 16px rgba(30, 58, 138, 0.08); padding-bottom: 10px;'>", unsafe_allow_html=True)
        st.plotly_chart(fig_inv_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Right Card: Position by Instrument (PKR Table) ---
    table_rows = ""
    for item in investment_data:
        table_rows += f"""
        <tr class="inv-row">
            <td style="padding: 14px 16px; border-bottom: 1px solid #E2E8F0; text-align: left; font-weight: 700; color: #0F172A;">{item['instrument']}</td>
            <td style="padding: 14px 16px; border-bottom: 1px solid #E2E8F0; text-align: right; font-weight: 600; color: #1E293B;">{item['value']:,.2f}</td>
            <td style="padding: 14px 16px; border-bottom: 1px solid #E2E8F0; text-align: right; font-weight: 800; color: #2563EB;">{item['conc']:.1f}%</td>
        </tr>
        """
        
    with inv_col2:
        st.markdown(f"""
            <style>
            .inv-row {{ transition: background-color 0.15s ease; }}
            .inv-row:hover {{ background-color: #F8FAFC; }}
            </style>
            
            <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px 20px; box-shadow: 0 6px 16px rgba(30, 58, 138, 0.08); height: 100%; display: flex; flex-direction: column;'>
                <div style='font-size: 18px; font-weight: 900; color: #0F172A; text-transform: uppercase;'>Position by Instrument</div>
                <div style='font-size: 13px; font-weight: 600; color: #64748B; margin-top: 4px; margin-bottom: 20px;'>Market Value & Concentration</div>
                
                <div style="flex-grow: 1; border-radius: 8px; overflow: hidden; border: 1px solid #E2E8F0;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 15px; background: white;">
                        <thead>
                            <tr style="background-color: #1E293B; color: #FFFFFF;">
                                <th style="padding: 14px 16px; text-align: left; font-weight: 800;">INSTRUMENT</th>
                                <th style="padding: 14px 16px; text-align: right; font-weight: 800;">MARKET VALUE (PKR Mns)</th>
                                <th style="padding: 14px 16px; text-align: right; font-weight: 800;">CONC. (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                        <tfoot>
                            <tr style="background-color: #F1F5F9;">
                                <td style="padding: 16px 16px; text-align: left; font-weight: 900; color: #0F172A;">Gross Portfolio</td>
                                <td style="padding: 16px 16px; text-align: right; font-weight: 900; color: #0F172A;">{gross_portfolio_value:,.2f}</td>
                                <td style="padding: 16px 16px; text-align: right; font-weight: 900; color: #2563EB;">100.0%</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        """, unsafe_allow_html=True)
