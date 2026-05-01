// API communication layer for Online Examination Platform

const API_BASE_URL = '/api';

// Get authentication token from localStorage
function getAuthToken() {
    return localStorage.getItem('access_token');
}

// Set authentication token
function setAuthToken(token) {
    localStorage.setItem('access_token', token);
}

// Get refresh token
function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

// Set refresh token
function setRefreshToken(token) {
    localStorage.setItem('refresh_token', token);
}

// Clear tokens
function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
}

// Make API request with authentication
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    const url = `${API_BASE_URL}${endpoint}`;

    const defaultOptions = {
        headers: {},
    };

    if (!(options.body instanceof FormData)) {
        defaultOptions.headers['Content-Type'] = 'application/json';
    }

    if (token) {
        defaultOptions.headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {}),
        },
    };

    try {
        const response = await fetch(url, config);

        // Handle token refresh if 401
        if (response.status === 401 && token) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                config.headers['Authorization'] = `Bearer ${getAuthToken()}`;
                return fetch(url, config);
            } else {
                clearTokens();
                window.location.href = '/frontend/login.html';
                throw new Error('Authentication failed');
            }
        }

        if (response.status === 204) {
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            let errorMsg = 'Request failed';

            if (data.error) {
                errorMsg = data.error;
            } else if (data.detail) {
                errorMsg = data.detail;
            } else if (typeof data === 'object') {
                // Handle DRF validation errors (e.g., {"field": ["Error content"]})
                const parts = [];
                for (const [key, value] of Object.entries(data)) {
                    const valStr = Array.isArray(value) ? value.join(', ') : String(value);
                    // Capitalize field name
                    const fieldName = key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ');
                    parts.push(`${fieldName}: ${valStr}`);
                }
                if (parts.length > 0) {
                    errorMsg = parts.join('\n');
                }
            }

            const error = new Error(errorMsg);
            error.data = data; // Attach original data for callers who can handle it
            throw error;
        }

        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Refresh access token
async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (response.ok) {
            const data = await response.json();
            setAuthToken(data.access);
            return true;
        }
    } catch (error) {
        console.error('Token refresh failed:', error);
    }

    return false;
}

// Users API
const usersAPI = {
    list: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return await apiRequest(`/auth/users/?${queryString}`);
    },

    get: async (id) => {
        return await apiRequest(`/auth/users/${id}/`);
    },

    create: async (data) => {
        return await apiRequest('/auth/users/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    update: async (id, data) => {
        return await apiRequest(`/auth/users/${id}/`, {
            method: 'PATCH', // Helper to use PATCH for partial updates
            body: JSON.stringify(data),
        });
    },

    delete: async (id) => {
        return await apiRequest(`/auth/users/${id}/`, {
            method: 'DELETE',
        });
    },
};

// Authentication API
const authAPI = {
    login: async (username, password) => {
        const data = await apiRequest('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        setAuthToken(data.access);
        setRefreshToken(data.refresh);
        if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
        }
        return data;
    },

    register: async (userData) => {
        const data = await apiRequest('/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
        setAuthToken(data.access);
        setRefreshToken(data.refresh);
        if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
        }
        return data;
    },

    logout: () => {
        try {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            localStorage.removeItem('refresh_token');
            window.location.href = '/frontend/login.html';
        } catch (e) {
            console.error('Logout error', e);
            window.location.href = '/frontend/login.html';
        }
    },

    getProfile: async () => {
        return await apiRequest('/auth/profile/');
    },

    updateProfile: async (data) => {
        const isFormData = data instanceof FormData;
        return await apiRequest('/auth/profile/', {
            method: 'PATCH', // Changed to PATCH to allow partial updates (files or text)
            body: isFormData ? data : JSON.stringify(data),
        });
    },
};

// Questions API
const questionsAPI = {
    list: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return await apiRequest(`/questions/?${queryString}`);
    },

    get: async (id) => {
        return await apiRequest(`/questions/${id}/`);
    },

    create: async (data) => {
        return await apiRequest('/questions/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    update: async (id, data) => {
        return await apiRequest(`/questions/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete: async (id) => {
        return await apiRequest(`/questions/${id}/`, {
            method: 'DELETE',
        });
    },

    getCategories: async () => {
        return await apiRequest('/questions/categories/');
    },
};

// Exams API
const examsAPI = {
    list: async () => {
        return await apiRequest('/exams/');
    },

    get: async (id) => {
        return await apiRequest(`/exams/${id}/`);
    },

    create: async (data) => {
        return await apiRequest('/exams/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    update: async (id, data) => {
        return await apiRequest(`/exams/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete: async (id) => {
        return await apiRequest(`/exams/${id}/`, {
            method: 'DELETE',
        });
    },

    getSchedule: async (examId) => {
        return await apiRequest(`/exams/${examId}/schedule/`);
    },

    updateSchedule: async (examId, data) => {
        return await apiRequest(`/exams/${examId}/schedule/`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
};

// Examinations API
const examinationsAPI = {
    startExam: async (examId) => {
        return await apiRequest('/examinations/start/', {
            method: 'POST',
            body: JSON.stringify({ exam_id: examId }),
        });
    },

    getSession: async (sessionId) => {
        return await apiRequest(`/examinations/sessions/${sessionId}/`);
    },

    submitAnswer: async (sessionId, answerData) => {
        return await apiRequest(`/examinations/sessions/${sessionId}/submit-answer/`, {
            method: 'POST',
            body: JSON.stringify(answerData),
        });
    },

    submitExam: async (sessionId) => {
        return await apiRequest(`/examinations/sessions/${sessionId}/submit/`, {
            method: 'POST',
        });
    },

    getSessions: async () => {
        return await apiRequest('/examinations/sessions/');
    },

    uploadSnapshot: async (sessionId, imageBlob) => {
        const formData = new FormData();
        formData.append('image', imageBlob, 'snapshot.jpg');

        const token = getAuthToken();
        const response = await fetch(`${API_BASE_URL}/examinations/sessions/${sessionId}/snapshot/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Snapshot upload failed');
        }
        return await response.json();
    },
};

// Results API
const resultsAPI = {
    list: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return await apiRequest(`/results/?${queryString}`);
    },

    get: async (id) => {
        return await apiRequest(`/results/${id}/`);
    },

    gradeSession: async (sessionId) => {
        return await apiRequest(`/results/sessions/${sessionId}/grade/`, {
            method: 'POST',
        });
    },

    getStatistics: async (examId) => {
        return await apiRequest(`/results/exams/${examId}/statistics/`);
    },

    getDashboardStats: async () => {
        return await apiRequest('/results/dashboard/stats/');
    },

    getAnalytics: async () => {
        return await apiRequest('/results/analytics/');
    },
};

// Notifications API
const notificationsAPI = {
    list: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return await apiRequest(`/notifications/?${queryString}`);
    },

    get: async (id) => {
        return await apiRequest(`/notifications/${id}/`);
    },

    markAsRead: async (id) => {
        return await apiRequest(`/notifications/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify({ is_read: true }),
        });
    },

    markAllAsRead: async () => {
        return await apiRequest('/notifications/mark-all-read/', {
            method: 'POST',
        });
    },

    getUnreadCount: async () => {
        return await apiRequest('/notifications/unread-count/');
    },
};

// Export APIs
window.API = {
    auth: authAPI,
    users: usersAPI,
    questions: questionsAPI,
    exams: examsAPI,
    examinations: examinationsAPI,
    results: resultsAPI,
    notifications: notificationsAPI,
    request: apiRequest,
};

