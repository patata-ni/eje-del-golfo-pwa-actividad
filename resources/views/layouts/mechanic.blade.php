<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Panel Mecánico | EJE del Golfo</title>
    <link rel="stylesheet" href="{{ asset('css/ejegolfo.css') }}">
</head>
<body class="admin-body">

    <!-- SIDEBAR -->
    <aside class="admin-sidebar">
        <div class="admin-logo">
            <a href="{{ url('/mechanic') }}">
                <svg class="bus-icon" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 5h26a5 5 0 0 1 5 5v25a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4V10a5 5 0 0 1 5-5Z" />
                    <path d="M7 25h34M12 10h24v11H12zM12 30h5m14 0h5" />
                    <circle cx="15" cy="38" r="3" />
                    <circle cx="33" cy="38" r="3" />
                </svg>
                <span>Taller EJE</span>
            </a>
        </div>

        <nav class="admin-menu">
            <p class="menu-label">PRINCIPAL</p>
            <a href="{{ route('mechanic.dashboard') }}" class="{{ request()->routeIs('mechanic.dashboard') ? 'active' : '' }}">Dashboard</a>
            
            <p class="menu-label">TALLER</p>
            <a href="{{ route('mechanic.reports.index') }}" class="{{ request()->routeIs('mechanic.reports.*') ? 'active' : '' }}">Reportes de Fallas</a>
            <a href="{{ route('mechanic.maintenance.index') }}" class="{{ request()->routeIs('mechanic.maintenance.*') ? 'active' : '' }}">Mantenimientos</a>
            <a href="{{ route('mechanic.inventory.index') }}" class="{{ request()->routeIs('mechanic.inventory.*') ? 'active' : '' }}">Inventario de Piezas</a>
            
            <p class="menu-label">CUENTA</p>
            <a href="{{ route('home') }}" target="_blank">Ver sitio web</a>
        </nav>

        <div class="admin-sidebar-footer">
            <form method="POST" action="{{ route('logout') }}">
                @csrf
                <button type="submit">Cerrar Sesión</button>
            </form>
        </div>
    </aside>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="admin-main">
        <header class="admin-topbar">
            <div class="search-bar">
                <input type="text" placeholder="Buscar unidad...">
            </div>
            <div class="admin-user-info">
                <span>Mecánico: {{ Auth::user()->name }}</span>
                <div class="avatar" style="background-color: #0fb541">{{ substr(Auth::user()->name, 0, 1) }}</div>
            </div>
        </header>

        <div class="admin-content">
            @yield('content')
        </div>
    </main>

    @stack('scripts')
<a href="{{ asset('pwa/index.html') }}" style="position:fixed;right:18px;bottom:18px;z-index:1000;padding:12px 18px;background:#073d32;color:white;border-radius:10px;font:600 13px system-ui;box-shadow:0 4px 20px #0002">Abrir bitácora PWA ↗</a>
</body>
</html>