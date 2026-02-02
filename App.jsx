import React, { useState, useEffect } from 'react';
import { Search, Bookmark, ExternalLink, X, LogIn, LogOut, Database, Plus, Trash2, ChevronLeft, ChevronRight, MapPin, DollarSign, Calendar, Building2 } from 'lucide-react';

// Sample data - Replace with API calls in production
const INITIAL_JOBS = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  title: [
    "Senior Blockchain Engineer",
    "Head of Marketing",
    "Enterprise Sales Manager",
    "Smart Contract Developer",
    "Product Designer",
    "Growth Hacker",
    "Security Engineer",
    "Community Manager",
    "Full Stack Engineer",
    "Business Development Lead"
  ][i % 10],
  company_name: [
    "Chainalysis",
    "Fireblocks",
    "Zero Hash",
    "Crypto.com",
    "IO Global",
    "Uniswap Labs",
    "Coinbase",
    "Polygon",
    "Alchemy",
    "Circle"
  ][i % 10],
  company_id: (i % 10) + 1,
  location: ["Remote", "New York, NY", "San Francisco, CA", "London, UK", "Singapore"][i % 5],
  salary: i % 3 === 0 ? null : `$${100 + i * 2}k - $${150 + i * 3}k`,
  sector: ["engineering", "marketing", "sales", "design", "operations"][i % 5],
  description: "Join our team to build the future of Web3. We're looking for talented individuals passionate about decentralized technology.",
  atsType: ["lever", "greenhouse", "ashby", "breezy", "workable"][i % 5],
  jobUrl: `https://example.com/job${i + 1}`,
  postedDate: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  skills: ["Solidity", "Rust", "React", "Node.js", "TypeScript", "Web3"].slice(0, Math.floor(Math.random() * 4) + 3)
}));

const INITIAL_COMPANIES = [
  {
    id: 1,
    name: "Chainalysis",
    website_url: "https://chainalysis.com",
    logo_url: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=100&h=100&fit=crop",
    job_board_url: "https://jobs.ashbyhq.com/chainalysis-careers",
    ats_type: "ashby",
    active: true
  },
  {
    id: 2,
    name: "Fireblocks",
    website_url: "https://fireblocks.com",
    logo_url: "https://images.unsplash.com/photo-1621504450181-5d356f61d307?w=100&h=100&fit=crop",
    job_board_url: "https://job-boards.greenhouse.io/fireblocks/",
    ats_type: "greenhouse",
    active: true
  },
  {
    id: 3,
    name: "Zero Hash",
    website_url: "https://zerohash.com",
    logo_url: "https://images.unsplash.com/photo-1605792657660-596af9009e82?w=100&h=100&fit=crop",
    job_board_url: "https://zero-hash.breezy.hr/",
    ats_type: "breezy",
    active: true
  }
];

const SECTORS = [
  { id: 'all', name: 'All Jobs' },
  { id: 'engineering', name: 'Engineering' },
  { id: 'sales', name: 'Sales' },
  { id: 'marketing', name: 'Marketing' },
  { id: 'design', name: 'Design' },
  { id: 'operations', name: 'Operations' }
];

const JOBS_PER_PAGE = 10;

export default function App() {
  const [jobs, setJobs] = useState(INITIAL_JOBS);
  const [companies, setCompanies] = useState(INITIAL_COMPANIES);
  const [filteredJobs, setFilteredJobs] = useState(INITIAL_JOBS);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSector, setSelectedSector] = useState('all');
  const [savedJobs, setSavedJobs] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);
  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const saved = localStorage.getItem('web3jobs_saved');
    const userData = localStorage.getItem('web3jobs_user');
    const adminData = localStorage.getItem('web3jobs_superadmin');
    
    if (saved) setSavedJobs(JSON.parse(saved));
    if (userData) {
      setUser(JSON.parse(userData));
      setIsLoggedIn(true);
    }
    if (adminData) {
      setIsSuperAdmin(true);
    }
  }, []);

  useEffect(() => {
    let filtered = jobs;

    if (selectedSector !== 'all') {
      filtered = filtered.filter(job => job.sector === selectedSector);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(job =>
        job.title.toLowerCase().includes(query) ||
        job.company_name.toLowerCase().includes(query) ||
        job.description.toLowerCase().includes(query) ||
        job.skills?.some(skill => skill.toLowerCase().includes(query))
      );
    }

    setFilteredJobs(filtered);
    setCurrentPage(1);
  }, [searchQuery, selectedSector, jobs]);

  const totalPages = Math.ceil(filteredJobs.length / JOBS_PER_PAGE);
  const startIndex = (currentPage - 1) * JOBS_PER_PAGE;
  const endIndex = startIndex + JOBS_PER_PAGE;
  const currentJobs = filteredJobs.slice(startIndex, endIndex);

  const toggleSaveJob = (jobId) => {
    if (!isLoggedIn) {
      setShowLogin(true);
      return;
    }

    const newSaved = savedJobs.includes(jobId)
      ? savedJobs.filter(id => id !== jobId)
      : [...savedJobs, jobId];
    
    setSavedJobs(newSaved);
    localStorage.setItem('web3jobs_saved', JSON.stringify(newSaved));
  };

  const handleLogin = (email, password) => {
    if (email === 'shardulbuzo@gmail.com' && password === 'birdisthewordA1$') {
      const adminUser = {
        name: 'Shardul (Admin)',
        email: email,
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin',
        isSuperAdmin: true
      };
      setUser(adminUser);
      setIsLoggedIn(true);
      setIsSuperAdmin(true);
      setShowLogin(false);
      localStorage.setItem('web3jobs_user', JSON.stringify(adminUser));
      localStorage.setItem('web3jobs_superadmin', 'true');
      return true;
    }
    return false;
  };

  const handleSocialLogin = (provider) => {
    const mockUser = {
      name: provider === 'google' ? 'John Doe' : 'Jane Smith',
      email: provider === 'google' ? 'john@gmail.com' : 'jane@linkedin.com',
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${provider}`,
      isSuperAdmin: false
    };
    setUser(mockUser);
    setIsLoggedIn(true);
    setIsSuperAdmin(false);
    setShowLogin(false);
    localStorage.setItem('web3jobs_user', JSON.stringify(mockUser));
    
    alert(`✅ Successfully signed in with ${provider === 'google' ? 'Google' : 'LinkedIn'}!\n\nWelcome, ${mockUser.name}!`);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setIsSuperAdmin(false);
    setUser(null);
    setSavedJobs([]);
    localStorage.removeItem('web3jobs_user');
    localStorage.removeItem('web3jobs_superadmin');
    localStorage.removeItem('web3jobs_saved');
  };

  const getCompanyLogo = (companyId) => {
    const company = companies.find(c => c.id === companyId);
    return company?.logo_url || 'https://via.placeholder.com/100';
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="fixed inset-0 opacity-[0.03] pointer-events-none" style={{
        backgroundImage: 'linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }}></div>

      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-black/80 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                <span className="text-black font-bold text-xl">W3</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Web3 Jobs</h1>
                <p className="text-xs text-gray-500">Decentralized Careers</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {isLoggedIn ? (
                <>
                  {isSuperAdmin && (
                    <button
                      onClick={() => setShowAdmin(true)}
                      className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white hover:bg-gray-800 transition-all"
                    >
                      <Database className="w-4 h-4" />
                      <span className="font-medium">Admin Panel</span>
                    </button>
                  )}
                  <div className="flex items-center space-x-3 bg-gray-900 rounded-lg px-3 py-2 border border-gray-800">
                    <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full" />
                    <div className="hidden sm:block">
                      <p className="text-sm font-medium text-white">{user.name}</p>
                      <p className="text-xs text-gray-500">{savedJobs.length} saved</p>
                    </div>
                    <button onClick={handleLogout} className="p-2 hover:bg-gray-800 rounded transition-colors">
                      <LogOut className="w-4 h-4 text-gray-400" />
                    </button>
                  </div>
                </>
              ) : (
                <button
                  onClick={() => setShowLogin(true)}
                  className="flex items-center space-x-2 px-6 py-2 rounded-lg bg-white text-black hover:bg-gray-200 transition-all transform hover:scale-105 font-medium"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Sign In</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative">
        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search jobs, companies, skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-gray-900 border border-gray-800 rounded-lg focus:outline-none focus:border-white transition-all text-white placeholder-gray-500"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            {SECTORS.map((sector) => (
              <button
                key={sector.id}
                onClick={() => setSelectedSector(sector.id)}
                className={`px-4 py-2 rounded-lg border transition-all ${
                  selectedSector === sector.id
                    ? 'bg-white text-black border-white'
                    : 'bg-gray-900 border-gray-800 text-gray-400 hover:border-gray-600'
                }`}
              >
                <span className="text-sm font-medium">{sector.name}</span>
              </button>
            ))}
          </div>

          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>{filteredJobs.length} opportunities found</p>
            <p className="text-gray-600">Showing {startIndex + 1}-{Math.min(endIndex, filteredJobs.length)} of {filteredJobs.length}</p>
          </div>
        </div>

        {/* Job Listings */}
        <div className="space-y-4 mb-8">
          {currentJobs.map((job) => (
            <div
              key={job.id}
              className="group relative bg-gray-950 border border-gray-800 rounded-lg p-6 hover:border-gray-600 transition-all"
            >
              <div className="flex items-start justify-between gap-6">
                <div className="flex items-start space-x-4 flex-1">
                  <img
                    src={getCompanyLogo(job.company_id)}
                    alt={job.company_name}
                    className="w-16 h-16 rounded-lg object-cover border border-gray-800 flex-shrink-0 bg-gray-900"
                  />
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="text-xl font-semibold text-white group-hover:text-gray-200 transition-colors mb-1">
                      {job.title}
                    </h3>
                    <p className="text-gray-400 font-medium mb-3">{job.company_name}</p>
                    
                    <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-3">
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-4 h-4" />
                        <span>{job.location}</span>
                      </div>
                      {job.salary && (
                        <div className="flex items-center space-x-1">
                          <DollarSign className="w-4 h-4" />
                          <span className="text-white font-medium">{job.salary}</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(job.postedDate).toLocaleDateString()}</span>
                      </div>
                      <span className="px-2 py-1 rounded text-xs bg-gray-800 text-gray-400 border border-gray-700">
                        {job.atsType}
                      </span>
                    </div>

                    <p className="text-gray-400 text-sm mb-3">{job.description}</p>

                    <div className="flex flex-wrap gap-2">
                      {job.skills?.map((skill, idx) => (
                        <span key={idx} className="px-2 py-1 text-xs rounded bg-gray-900 text-gray-300 border border-gray-800">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex flex-col items-end space-y-3">
                  <button
                    onClick={() => toggleSaveJob(job.id)}
                    className="p-3 rounded-lg bg-gray-900 hover:bg-gray-800 border border-gray-800 transition-all"
                  >
                    <Bookmark className={`w-5 h-5 ${savedJobs.includes(job.id) ? 'fill-white' : ''}`} />
                  </button>

                  <a
                    href={job.jobUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 px-6 py-3 rounded-lg bg-white text-black hover:bg-gray-200 transition-all transform hover:scale-105 font-medium"
                  >
                    <span>View & Apply</span>
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center space-x-2 mt-8">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 rounded-lg bg-gray-900 border border-gray-800 text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            {[...Array(totalPages)].map((_, i) => {
              const page = i + 1;
              if (
                page === 1 ||
                page === totalPages ||
                (page >= currentPage - 1 && page <= currentPage + 1)
              ) {
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`w-10 h-10 rounded-lg font-medium transition-all ${
                      currentPage === page
                        ? 'bg-white text-black'
                        : 'bg-gray-900 border border-gray-800 text-gray-400 hover:bg-gray-800'
                    }`}
                  >
                    {page}
                  </button>
                );
              } else if (page === currentPage - 2 || page === currentPage + 2) {
                return <span key={page} className="text-gray-600">...</span>;
              }
              return null;
            })}

            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg bg-gray-900 border border-gray-800 text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {filteredJobs.length === 0 && (
          <div className="text-center py-20">
            <div className="w-20 h-20 mx-auto mb-4 bg-gray-900 rounded-full flex items-center justify-center border border-gray-800">
              <Search className="w-10 h-10 text-gray-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-400 mb-2">No jobs found</h3>
            <p className="text-gray-600">Try adjusting your search or filters</p>
          </div>
        )}
      </main>

      {showLogin && (
        <LoginModal
          onClose={() => setShowLogin(false)}
          onLogin={handleLogin}
          onSocialLogin={handleSocialLogin}
        />
      )}

      {showAdmin && isSuperAdmin && (
        <SuperAdminPanel
          companies={companies}
          setCompanies={setCompanies}
          jobs={jobs}
          onClose={() => setShowAdmin(false)}
        />
      )}
    </div>
  );
}

function LoginModal({ onClose, onLogin, onSocialLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const success = onLogin(email, password);
    if (!success) {
      setError('Invalid credentials. Only superadmin can login with email/password.');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-950 rounded-xl max-w-md w-full p-8 border border-gray-800 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Sign In</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-900 rounded-lg transition-colors">
            <X className="w-6 h-6 text-gray-400" />
          </button>
        </div>

        <p className="text-gray-400 mb-6">Sign in to save jobs and track applications</p>

        <form onSubmit={handleSubmit} className="space-y-4 mb-6">
          <input
            type="email"
            placeholder="Email (Superadmin only)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white placeholder-gray-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white placeholder-gray-500"
          />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-all font-medium text-white"
          >
            Admin Login
          </button>
        </form>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-800"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-gray-950 text-gray-500">Or continue with</span>
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => onSocialLogin('google')}
            className="w-full flex items-center justify-center space-x-3 px-6 py-3 bg-white text-black rounded-lg hover:bg-gray-200 transition-all font-medium"
          >
            <span>Continue with Google</span>
          </button>

          <button
            onClick={() => onSocialLogin('linkedin')}
            className="w-full flex items-center justify-center space-x-3 px-6 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg hover:bg-gray-800 transition-all font-medium"
          >
            <span>Continue with LinkedIn</span>
          </button>
        </div>
      </div>
    </div>
  );
}

function SuperAdminPanel({ companies, setCompanies, jobs, onClose }) {
  const [activeTab, setActiveTab] = useState('companies');
  const [newCompany, setNewCompany] = useState({
    name: '',
    website_url: '',
    logo_url: '',
    job_board_url: '',
    ats_type: 'lever',
    description: ''
  });

  const addCompany = () => {
    if (!newCompany.name || !newCompany.job_board_url) {
      alert('Please fill in at least Company Name and Job Board URL');
      return;
    }
    
    const company = {
      ...newCompany,
      id: Math.max(...companies.map(c => c.id), 0) + 1,
      active: true
    };
    setCompanies([...companies, company]);
    setNewCompany({
      name: '',
      website_url: '',
      logo_url: '',
      job_board_url: '',
      ats_type: 'lever',
      description: ''
    });
    alert(`✅ Company "${company.name}" added successfully!`);
  };

  const deleteCompany = (id) => {
    if (window.confirm('Are you sure you want to delete this company?')) {
      setCompanies(companies.map(c => 
        c.id === id ? { ...c, active: false } : c
      ));
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-gray-950 rounded-xl max-w-6xl w-full my-8 border border-gray-800 shadow-2xl">
        <div className="sticky top-0 bg-gray-950 border-b border-gray-800 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">Superadmin Panel</h2>
            <p className="text-gray-500 text-sm">Manage companies and view database</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-900 rounded-lg transition-colors">
            <X className="w-6 h-6 text-gray-400" />
          </button>
        </div>

        <div className="p-6">
          <div className="flex space-x-2 mb-6 border-b border-gray-800">
            <button
              onClick={() => setActiveTab('companies')}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === 'companies'
                  ? 'text-white border-b-2 border-white'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Building2 className="w-4 h-4" />
                <span>Companies ({companies.filter(c => c.active).length})</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('jobs')}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === 'jobs'
                  ? 'text-white border-b-2 border-white'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4" />
                <span>Jobs Database ({jobs.length})</span>
              </div>
            </button>
          </div>

          {activeTab === 'companies' && (
            <div className="space-y-6">
              <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                <h3 className="text-lg font-bold text-white mb-4">Add New Company</h3>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Company Name *"
                    value={newCompany.name}
                    onChange={(e) => setNewCompany({...newCompany, name: e.target.value})}
                    className="px-4 py-3 bg-black border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white placeholder-gray-500"
                  />
                  <input
                    type="text"
                    placeholder="Website URL"
                    value={newCompany.website_url}
                    onChange={(e) => setNewCompany({...newCompany, website_url: e.target.value})}
                    className="px-4 py-3 bg-black border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white placeholder-gray-500"
                  />
                  <input
                    type="text"
                    placeholder="Logo URL"
                    value={newCompany.logo_url}
                    onChange={(e) => setNewCompany({...newCompany, logo_url: e.target.value})}
                    className="px-4 py-3 bg-black border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white placeholder-gray-500"
                  />
                  <input
                    type="text"
                    placeholder="Job Board URL *"
                    value={newCompany.job_board_url}
                    onChange={(e) => setNewCompany({...newCompany, job_board_url: e.target.value})}
                    className="px-4 py-3 bg-black border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white placeholder-gray-500"
                  />
                  <select
                    value={newCompany.ats_type}
                    onChange={(e) => setNewCompany({...newCompany, ats_type: e.target.value})}
                    className="px-4 py-3 bg-black border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white"
                  >
                    <option value="lever">Lever</option>
                    <option value="greenhouse">Greenhouse</option>
                    <option value="ashby">Ashby</option>
                    <option value="breezy">Breezy</option>
                    <option value="workable">Workable</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Description"
                    value={newCompany.description}
                    onChange={(e) => setNewCompany({...newCompany, description: e.target.value})}
                    className="px-4 py-3 bg-black border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white placeholder-gray-500"
                  />
                </div>
                <button
                  onClick={addCompany}
                  className="mt-4 w-full flex items-center justify-center space-x-2 px-6 py-3 bg-white text-black hover:bg-gray-200 rounded-lg transition-all font-medium"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Company</span>
                </button>
              </div>

              <div>
                <h3 className="text-lg font-bold text-white mb-4">Active Companies</h3>
                <div className="space-y-3">
                  {companies.filter(c => c.active).map((company) => (
                    <div key={company.id} className="flex items-center justify-between p-4 bg-gray-900 rounded-lg border border-gray-800">
                      <div className="flex items-center space-x-4">
                        {company.logo_url && (
                          <img src={company.logo_url} alt={company.name} className="w-12 h-12 rounded-lg object-cover bg-black" />
                        )}
                        <div>
                          <p className="font-medium text-white">{company.name}</p>
                          <p className="text-sm text-gray-500">{company.job_board_url}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="px-3 py-1 rounded text-sm font-medium bg-gray-800 text-gray-400 border border-gray-700">
                          {company.ats_type}
                        </div>
                        <button
                          onClick={() => deleteCompany(company.id)}
                          className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'jobs' && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                  <p className="text-sm text-gray-400 mb-2">Total Jobs</p>
                  <p className="text-3xl font-bold text-white">{jobs.length}</p>
                </div>
                <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                  <p className="text-sm text-gray-400 mb-2">Active Companies</p>
                  <p className="text-3xl font-bold text-white">{companies.filter(c => c.active).length}</p>
                </div>
                <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                  <p className="text-sm text-gray-400 mb-2">Jobs This Month</p>
                  <p className="text-3xl font-bold text-white">
                    {jobs.filter(j => {
                      const date = new Date(j.postedDate);
                      const now = new Date();
                      return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
                    }).length}
                  </p>
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto space-y-2">
                {jobs.slice(0, 20).map((job) => (
                  <div key={job.id} className="p-4 bg-gray-900 rounded-lg border border-gray-800">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-white">{job.title}</p>
                        <p className="text-sm text-gray-500">{job.company_name} • {job.location}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-400">{job.sector}</p>
                        <p className="text-xs text-gray-600">{new Date(job.postedDate).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
