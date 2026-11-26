<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Transportes EJE del Golfo</title>
    <link rel="stylesheet" href="{{ asset('css/ejegolfo.css') }}">
    <style>
        /* --- ARREGLO DEL HEADER Y MENÚ DE USUARIO --- */
        header {
            background-color: var(--verde-bosque);
            color: var(--blanco);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap; /* Para que no se rompa en pantallas pequeñas */
            gap: 1rem;
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 2rem; /* Separación entre el menú y el usuario */
        }

        .main-nav {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .main-nav a {
            color: var(--blanco);
            font-weight: 500;
            transition: color 0.3s;
        }

        .main-nav a:hover {
            color: var(--verde-menta);
        }

        /* Sección del usuario */
        .user-menu {
            display: flex;
            align-items: center;
            gap: 1rem;
            border-left: 1px solid rgba(255, 255, 255, 0.2); /* Línea divisoria */
            padding-left: 2rem;
        }

        .header-user {
            color: var(--verde-menta);
            font-weight: 600;
            font-size: 0.9rem;
        }

        /* Botón "Ir al Panel" */
        .btn-panel {
            background-color: transparent;
            color: var(--verde-menta);
            border: 1px solid var(--verde-esmeralda);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.3s;
        }

        .btn-panel:hover {
            background-color: var(--verde-esmeralda);
            color: var(--blanco);
        }

        /* Botón "Cerrar Sesión" (Ya no es rojo, ahora es elegante) */
        .btn-logout {
            background-color: rgba(255, 255, 255, 0.1); /* Fondo sutil */
            color: var(--blanco);
            border: 1px solid transparent;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }

        .btn-logout:hover {
            background-color: #e74c3c; /* Solo se pone rojo cuando pasas el mouse (opcional) */
            color: white;
        }

        .logout-form {
            margin: 0;
            display: inline-flex;
        }

        /* Ajuste para móviles */
        @media (max-width: 900px) {
            .header-right {
                flex-direction: column;
                align-items: flex-end;
                gap: 1rem;
            }
            .user-menu {
                border-left: none;
                padding-left: 0;
                border-top: 1px solid rgba(255, 255, 255, 0.2);
                padding-top: 1rem;
            }
        }
    </style>
</head>
<body>
        <header>
        <a href="{{ route('home') }}" class="logo">
            <svg class="bus-icon" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M11 5h26a5 5 0 0 1 5 5v25a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4V10a5 5 0 0 1 5-5Z" />
                <path d="M7 25h34M12 10h24v11H12zM12 30h5m14 0h5" />
                <circle cx="15" cy="38" r="3" />
                <circle cx="33" cy="38" r="3" />
            </svg>
            <span>EJE del Golfo</span>
        </a>

        <!-- Contenedor de navegación y usuario -->
        <div class="header-right">
            <nav class="main-nav">
                <a href="{{ route('home') }}">Inicio</a>
                <a href="{{ route('rutas') }}">Rutas y Horarios</a>
                <a href="{{ route('nosotros') }}">Nosotros</a>
                <a href="{{ route('ayuda') }}">Ayuda</a>
            </nav>

            @auth
                <div class="user-menu">
                    <span class="header-user">{{ Auth::user()->name }}</span>

                    @if(Auth::user()->role_id == 1 || Auth::user()->role_id == 2)
                        <a href="{{ url('/admin') }}" class="btn-panel">
                            Ir al Panel
                        </a>
                    @endif

                    <form method="POST" action="{{ route('logout') }}" class="logout-form">
                        @csrf
                        <button type="submit" class="btn-logout">Cerrar Sesión</button>
                    </form>
                </div>
            @else
                <a href="{{ route('login') }}" class="btn-login">Iniciar Sesión</a>
            @endauth
        </div>
    </header>

    <main>
        @yield('content')
    </main>

    <footer class="site-footer">
        <div class="footer-main">
            <div class="footer-brand-block">
                <a href="{{ route('home') }}" class="footer-logo">
                    <svg class="bus-icon" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M11 5h26a5 5 0 0 1 5 5v25a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4V10a5 5 0 0 1 5-5Z" />
                        <path d="M7 25h34M12 10h24v11H12zM12 30h5m14 0h5" />
                        <circle cx="15" cy="38" r="3" />
                        <circle cx="33" cy="38" r="3" />
                    </svg>
                    <span>EJE del Golfo</span>
                </a>
                <p>Conectamos Poza Rica y Martínez de la Torre con un servicio seguro, puntual y cercano.</p>
            </div>
            <nav class="footer-links" aria-label="Información">
                <h2>Información</h2>
                <a href="{{ route('rutas') }}">Rutas y horarios</a>
                <a href="{{ route('nosotros') }}">Nosotros</a>
                <a href="{{ route('ayuda') }}#contacto">Contacto</a>
            </nav>
            <nav class="footer-links" aria-label="Legal">
                <h2>Legal</h2>
                <a href="{{ route('privacidad') }}">Política de privacidad</a>
                <a href="{{ route('terminos') }}">Términos</a>
            </nav>
        </div>
        <div class="footer-bottom">
            <p>&copy; {{ date('Y') }} Transportes EJE del Golfo. Todos los derechos reservados.</p>
        </div>
    </footer>
    @stack('scripts')
<a href="{{ asset('pwa/index.html') }}" style="position:fixed;right:18px;bottom:18px;z-index:1000;padding:12px 18px;background:#073d32;color:white;border-radius:10px;font:600 13px system-ui;box-shadow:0 4px 20px #0002">Abrir bitácora PWA ↗</a>
</body>
</html>
