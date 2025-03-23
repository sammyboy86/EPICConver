import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from openai import OpenAI
import time
import base64


# Load configuration
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Add logo to the top right of every page
def add_logo():
    col1, col2 = st.columns([4, 1])  # Adjust column widths as needed
    with col1:
        st.title("EPIC Conver: Converjamos nuevamente")  # Main title
    with col2:
        st.image("media/logo.jpeg", width=100)  # Display logo on the top right

# Display the logo and title
add_logo()

# Initialize the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Attempt to login
try:
    authenticator.login(fields={'Form name': 'EPIC Conver: Inicio'})  # Add login title
except Exception as e:
    st.error(e)

# Check login status
if st.session_state.get('authentication_status'):
    authenticator.logout()
    st.write(f'Te damos la bienvenida, *{st.session_state.get("name")}*')

    # Initialize session state for page navigation and personas
    if 'page' not in st.session_state:
        st.session_state.page = 'input_page'
    if 'personas' not in st.session_state:
        st.session_state.personas = None

    # Input pag
    if st.session_state.page == 'input_page':
        # Mostrar encabezado
        st.header("Conectemos para crecer")

        # Crear dos columnas: video a la izquierda, espacio a la derecha (aunque no se use)
        video_col, _ = st.columns([3, 1])

        with video_col:
            st.video("media/bienvenida.mp4")

        # Mostrar campo de descripción inmediatamente
        st.markdown("### Describe lo que te apasiona del emprendimiento y tu experiencia emprendiendo:")
        user_input = st.text_area("Escribe tu descripción aquí", height=200)

        if st.button('Conectar experiencia'):
            if user_input:
                # Load the OpenAI API key from config.yaml
                api_key = st.secrets["my_api"]["key"]

                # Initialize the OpenAI client with the API key
                client = OpenAI(api_key=api_key)

                # Define the prompt for OpenAI
                prompt = f"""
                [Descripción escrita por el usuario]
                {user_input}

                Crea 3 descripciones de personas (Jayce, Caitlyn, Vi) que sean similares a la descripción anterior; enfócate en vocabulario orientado al emprendimiento, pero haz que cada persona sea única. IMPORTANTE: Separa cada descripción con una línea en blanco (no agregues símbolos a las separaciones).
                """

               # Send the prompt to ChatGPT
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,  # Puedes subir esto si lo necesitas
                    temperature=0.8  # Da un poco más de variedad
                )

                # Validar que haya una respuesta adecuada
                if response and response.choices and response.choices[0].message and response.choices[0].message.content:
                    personas_text = response.choices[0].message.content.strip()
                    personas = personas_text.split("\n\n")
                    
                    # Validar que haya exactamente 3 descripciones
                    if len(personas) == 3:
                        st.session_state.personas = personas_text
                        st.session_state.page = 'result_page'
                        st.rerun()
                    else:
                        st.error(personas_text)
                        st.error("La respuesta no contenía 3 descripciones claras. Por favor, intenta nuevamente o mejora la descripción.")
                else:
                    st.error("No se pudo obtener una respuesta válida de la API. Intenta de nuevo más tarde.")

            except Exception as e:
                st.error(f"Ocurrió un error al llamar a OpenAI: {e}")

            else:
                st.error("Por favor, escribe una descripción.")

    # Result page
    elif st.session_state.page == 'result_page':
        st.header("Vínculos latentes")

        for key in ['show_jayce_input', 'show_caitlyn_input', 'show_vi_input']:
            if key not in st.session_state:
                st.session_state[key] = False


        # Split the generated personas into individual descriptions
        personas = st.session_state.personas.split("\n\n")  # Split by double newlines

        # Ensure there are exactly 3 personas
        if len(personas) == 3:
            # Jayce's Container
            with st.container():
                col1, col2 = st.columns([1, 3])  # Split container into two columns
                with col1:
                    st.image("media/jayce.webp", width=150)  # Display Jayce's profile picture
                with col2:
                    st.subheader("Jayce")
                    st.info(personas[0])  # Display Jayce's description in a box

                    # Initialize session state for Jayce's input box visibility
                    if 'show_jayce_input' not in st.session_state:
                        st.session_state.show_jayce_input = False

                    # Toggle input box visibility when "Enviar Mensaje" is clicked
                    if st.button("Enviar Mensaje a Jayce", key="jayce_button"):
                        st.session_state.show_jayce_input = not st.session_state.show_jayce_input

                    # Show input box and send button if visibility is True
                    if st.session_state.show_jayce_input:
                        message = st.text_input("Escribe tu mensaje para Jayce:", key="jayce_input")
                        if st.button("Enviar", key="jayce_send"):
                            st.session_state.show_jayce_input = False  # Hide input box
                            st.success(f"Mensaje enviado a Jayce")  # Notify user

            # Caitlyn's Container
            with st.container():
                col1, col2 = st.columns([1, 3])  # Split container into two columns
                with col1:
                    st.image("media/caitlyn.webp", width=150)  # Display Caitlyn's profile picture
                with col2:
                    st.subheader("Caitlyn")
                    st.info(personas[1])  # Display Caitlyn's description in a box

                    # Initialize session state for Caitlyn's input box visibility
                    if 'show_caitlyn_input' not in st.session_state:
                        st.session_state.show_caitlyn_input = False

                    # Toggle input box visibility when "Enviar Mensaje" is clicked
                    if st.button("Enviar Mensaje a Caitlyn", key="caitlyn_button"):
                        st.session_state.show_caitlyn_input = not st.session_state.show_caitlyn_input

                    # Show input box and send button if visibility is True
                    if st.session_state.show_caitlyn_input:
                        message = st.text_input("Escribe tu mensaje para Caitlyn:", key="caitlyn_input")
                        if st.button("Enviar", key="caitlyn_send"):
                            st.session_state.show_caitlyn_input = False  # Hide input box
                            st.success(f"Mensaje enviado a Caitlyn")  # Notify user

            # Vi's Container
            with st.container():
                col1, col2 = st.columns([1, 3])  # Split container into two columns
                with col1:
                    st.image("media/vi.jpg", width=150)  # Display Vi's profile picture
                with col2:
                    st.subheader("Vi")
                    st.info(personas[2])  # Display Vi's description in a box

                    # Initialize session state for Vi's input box visibility
                    if 'show_vi_input' not in st.session_state:
                        st.session_state.show_vi_input = False

                    # Toggle input box visibility when "Enviar Mensaje" is clicked
                    if st.button("Enviar Mensaje a Vi", key="vi_button"):
                        st.session_state.show_vi_input = not st.session_state.show_vi_input

                    # Show input box and send button if visibility is True
                    if st.session_state.show_vi_input:
                        message = st.text_input("Escribe tu mensaje para Vi:", key="vi_input")
                        if st.button("Enviar", key="vi_send"):
                            st.session_state.show_vi_input = False  # Hide input box
                            st.success(f"Mensaje enviado a Vi")  # Notify user
        else:
            pass
            #show error
            #st.error("No se pudieron generar las descripciones correctamente. Por favor, intenta con una descripción más detallada.")
        

        # Add a back button to return to the input page
        if st.button('Volver a la Descripción'):
            st.session_state.page = 'input_page'
            st.rerun()  # Force a rerun to update the UI immediately

elif st.session_state.get('authentication_status') is False:
    st.error('Usuario/contraseña incorrectos')
elif st.session_state.get('authentication_status') is None:
    st.warning('Por favor, ingresa tu usuario y contraseña')