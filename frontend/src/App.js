import React from 'react';
import './App.css';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import JobDetail from './pages/JobDetail';
import ListPage from './pages/ListPage';
import Contact from './pages/Contact';
import About from './pages/About';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import { Toaster } from './components/ui/toaster';

const Layout = ({ children }) => {
  const loc = useLocation();
  const isAdmin = loc.pathname.startsWith('/admin');
  return (
    <div className="App">
      {!isAdmin && <Header />}
      {isAdmin && (
        <div className="bg-purple-950 text-white py-3 px-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="font-extrabold">AssamVacancies Admin</div>
            <a href="/" className="text-sm text-purple-200 hover:text-white">← Back to site</a>
          </div>
        </div>
      )}
      <main className="min-h-[60vh]">{children}</main>
      {!isAdmin && <Footer />}
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/job/:id" element={<JobDetail />} />
            <Route path="/category/:category" element={<ListPage />} />
            <Route path="/type/:type" element={<ListPage />} />
            <Route path="/search" element={<ListPage />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/about" element={<About />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </Layout>
        <Toaster />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
