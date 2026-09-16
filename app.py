# 2. Splash Screen
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; text-align: center; background-color: #0f6286; animation: fadeOut 0.8s ease-in 4.5s forwards; position: fixed; top: 0; left: 0; width: 100%; z-index: 9999999;'>
                
                <!-- Logo with glowing pulse -->
                <img src="krn logo.jpg" alt="Karandaaz Logo" style="width: 250px; margin-bottom: 30px; border-radius: 8px; animation: pulseLogo 2s ease-in-out infinite;" onerror="this.style.display='none'">
                
                <!-- Headings -->
                <h1 style='color: #FFFFFF; font-size: 48px; letter-spacing: 1px; margin-bottom: 12px; font-weight: 700; font-family: "Chivo", sans-serif;'>Karandaaz Treasury Portfolio</h1>
                <p style='color: #f68b1e; font-size: 20px; font-weight: 400; letter-spacing: 0.5px; margin-bottom: 40px; font-family: "Chivo", sans-serif;'>Initializing Financial Models & Data...</p>
                
                <!-- Animated Financial Bar Chart Loader -->
                <div class="chart-loader">
                    <div class="bar bar1"></div>
                    <div class="bar bar2"></div>
                    <div class="bar bar3"></div>
                    <div class="bar bar4"></div>
                    <div class="bar bar5"></div>
                </div>
                
                <!-- Sleek Progress Bar -->
                <div class="progress-container">
                    <div class="progress-bar"></div>
                </div>
                
            </div>
            
            <style>
            /* Financial Bar Chart Animation */
            .chart-loader {
                display: flex;
                align-items: flex-end;
                gap: 8px;
                height: 60px;
                margin-bottom: 30px;
            }
            .bar {
                width: 12px;
                background-color: #f68b1e;
                border-radius: 4px 4px 0 0;
                animation: growBar 1s ease-in-out infinite alternate;
                transform-origin: bottom;
            }
            .bar1 { height: 30%; animation-delay: 0.0s; }
            .bar2 { height: 60%; animation-delay: 0.2s; }
            .bar3 { height: 100%; animation-delay: 0.4s; }
            .bar4 { height: 50%; animation-delay: 0.6s; }
            .bar5 { height: 80%; animation-delay: 0.8s; }

            @keyframes growBar {
                0% { transform: scaleY(0.3); opacity: 0.7; }
                100% { transform: scaleY(1); opacity: 1; box-shadow: 0 0 10px rgba(246, 139, 30, 0.6); }
            }

            /* Progress Bar Animation */
            .progress-container {
                width: 320px;
                height: 6px;
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                overflow: hidden;
                position: relative;
            }
            .progress-bar {
                width: 0%;
                height: 100%;
                background-color: #f68b1e;
                /* Matches the 4.5s wait before fade out */
                animation: loadProgress 4.5s cubic-bezier(0.4, 0, 0.2, 1) forwards; 
            }

            @keyframes loadProgress {
                0% { width: 0%; }
                30% { width: 45%; }
                70% { width: 80%; }
                100% { width: 100%; }
            }

            /* Logo & Fade Out Keyframes */
            @keyframes pulseLogo { 
                0% { transform: scale(0.98); opacity: 0.9; } 
                50% { transform: scale(1.02); opacity: 1; filter: drop-shadow(0 0 15px rgba(246, 139, 30, 0.4));} 
                100% { transform: scale(0.98); opacity: 0.9; } 
            }
            @keyframes fadeOut { 
                0% { opacity: 1; visibility: visible; } 
                100% { opacity: 0; visibility: hidden; } 
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Forces Streamlit to wait exactly 5 seconds while the animation plays
        time.sleep(5.0) 
        
    splash.empty()
    st.session_state.first_load = False
