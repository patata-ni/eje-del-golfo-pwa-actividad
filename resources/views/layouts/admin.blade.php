<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Panel Admin | Eje del Golfo</title>
    <link rel="stylesheet" href="{{ asset('css/ejegolfo.css') }}">
</head>
<body class="admin-body">

    <!-- SIDEBAR -->
    <aside class="admin-sidebar">
        <div class="admin-logo">
            <a href="{{ url('/admin') }}">
                <svg class="bus-icon" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 5h26a5 5 0 0 1 5 5v25a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4V10a5 5 0 0 1 5-5Z" />
                    <path d="M7 25h34M12 10h24v11H12zM12 30h5m14 0h5" />
                    <circle cx="15" cy="38" r="3" />
                    <circle cx="33" cy="38" r="3" />
                </svg>
                <span>EJE Admin</span>
            </a>
        </div>

        <nav class="admin-menu">
            <p class="menu-label">PRINCIPAL</p>
            <a href="{{ url('/admin') }}" class="{{ request()->is('admin') ? 'active' : '' }}">Dashboard</a>
            <a href="{{ route('admin.messages.clients') }}" class="{{ request()->routeIs('admin.messages.clients') ? 'active' : '' }}">Buzón de Clientes</a>
            
            <p class="menu-label">OPERACIONES</p>
            <a href="{{ route('admin.units.index') }}" class="{{ request()->routeIs('admin.units.*') ? 'active' : '' }}">Unidades</a>
            <a href="{{ route('admin.routes.index') }}" class="{{ request()->routeIs('admin.routes.*') ? 'active' : '' }}">Rutas y Paradas</a>
            <a href="{{ route('admin.schedules.index') }}" class="{{ request()->routeIs('admin.schedules.*') ? 'active' : '' }}">Horarios Base</a>
            <a href="{{ route('admin.departures.index') }}" class="{{ request()->routeIs('admin.departures.*') ? 'active' : '' }}">Salidas</a>
            <a href="{{ route('admin.staff.index') }}" class="{{ request()->routeIs('admin.staff.*') ? 'active' : '' }}">Personal</a>
            <a href="{{ route('admin.drivers.index') }}" class="{{ request()->routeIs('admin.drivers.*') ? 'active' : '' }}">Choferes</a>
            <a href="{{ route('admin.users.index') }}" class="{{ request()->routeIs('admin.users.*') ? 'active' : '' }}">Accesos al Sistema</a>
            
            <p class="menu-label">MANTENIMIENTO</p>
            <a href="{{ route('admin.incidents.index') }}" class="{{ request()->routeIs('admin.incidents.*') ? 'active' : '' }}">Incidencias</a>
            <a href="#">Mantenimientos</a>
            <a href="{{ route('admin.inventory.index') }}" class="{{ request()->routeIs('admin.inventory.*') ? 'active' : '' }}">Inventario</a>
            <a href="{{ route('admin.notifications.index') }}" class="{{ request()->routeIs('admin.notifications.*') ? 'active' : '' }}">Notificaciones</a>
        </nav>

        <div class="admin-sidebar-footer">
            <a href="{{ route('home') }}" target="_blank">Ver sitio web</a>
            <form method="POST" action="{{ route('logout') }}">
                @csrf
                <button type="submit">Cerrar Sesión</button>
            </form>
        </div>
    </aside>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="admin-main">
        <!-- BARRA SUPERIOR -->
        <header class="admin-topbar">
            <div class="search-bar">
                <input type="text" placeholder="Buscar en el sistema...">
            </div>
            <div class="admin-user-info">
                <span>Hola, {{ Auth::user()->name }}</span>
                <div class="avatar">{{ substr(Auth::user()->name, 0, 1) }}</div>
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