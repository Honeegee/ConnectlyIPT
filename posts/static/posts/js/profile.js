// Get CSRF token once and store it
let csrfToken = null;

function getCsrfToken() {
    if (!csrfToken) {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            csrfToken = tokenElement.value;
        }
    }
    return csrfToken;
}

// Safely escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize CSRF token
    csrfToken = getCsrfToken();

    // Load profile if we're on the profile page
    if (window.location.pathname.includes('/profile/')) {
        const username = document.body.getAttribute('data-username');
        if (username) {
            loadProfile(username);
        }
    }

    // Handle tab clicks
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const tab = button.getAttribute('data-tab');
            if (tab) {
                switchTab(tab);
            }
        });
    });

    // Handle file inputs
    const editAvatarButton = document.querySelector('.edit-avatar');
    const editCoverButton = document.querySelector('.edit-cover');

    if (editAvatarButton) {
        editAvatarButton.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = handleAvatarChange;
            input.click();
        });
    }

    if (editCoverButton) {
        editCoverButton.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = handleCoverChange;
            input.click();
        });
    }
});

function handleAvatarChange(event) {
    const file = event.target.files[0];
    if (file) {
        window.selectedAvatar = file;
        const avatarImg = document.querySelector('.avatar-large');
        avatarImg.src = URL.createObjectURL(file);
    }
}

function handleCoverChange(event) {
    const file = event.target.files[0];
    if (file) {
        window.selectedCover = file;
        const coverImg = document.querySelector('.cover-photo');
        coverImg.src = URL.createObjectURL(file);
    }
}

async function loadProfile(username) {
    const mainContent = document.querySelector('.main-content');
    if (!mainContent) return;

    try {
        const loadingEl = document.createElement('div');
        loadingEl.className = 'loading';
        loadingEl.textContent = 'Loading profile...';
        mainContent.appendChild(loadingEl);

        const response = await fetch(`/api/profiles/${username}/`, {
            credentials: 'include',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        loadingEl.remove();

        // Update profile information
        const fullNameEl = document.querySelector('.profile-details h1');
        const usernameEl = document.querySelector('.profile-details .username');
        const bioEl = document.querySelector('.profile-details .bio');
        const postsCountEl = document.querySelector('.profile-stats .stat:nth-child(1) .stat-number');
        const followersCountEl = document.querySelector('.profile-stats .stat:nth-child(2) .stat-number');
        const followingCountEl = document.querySelector('.profile-stats .stat:nth-child(3) .stat-number');

        // Update text content
        if (fullNameEl) fullNameEl.textContent = data.full_name || username;
        if (usernameEl) usernameEl.textContent = `@${username}`;
        if (bioEl) bioEl.textContent = data.bio || '';
        if (postsCountEl) postsCountEl.textContent = data.posts_count || 0;
        if (followersCountEl) followersCountEl.textContent = data.followers_count || 0;
        if (followingCountEl) followingCountEl.textContent = data.following_count || 0;

        // Update profile images if available
        const avatarImg = document.querySelector('.avatar-large');
        const coverImg = document.querySelector('.cover-photo');
        if (avatarImg && data.avatar_url) avatarImg.src = data.avatar_url;
        if (coverImg && data.cover_url) coverImg.src = data.cover_url;

        // Handle button visibility and form data based on user
        const currentUser = document.body.getAttribute('data-username');
        const editProfileButton = document.querySelector('.edit-profile-button');
        const followButton = document.querySelector('.follow-button');
        const editCoverButton = document.querySelector('.edit-cover');
        const editAvatarButton = document.querySelector('.edit-avatar');

        if (username === currentUser) {
            // Show edit buttons for own profile
            if (editProfileButton) editProfileButton.style.display = 'block';
            if (followButton) followButton.style.display = 'none';
            if (editCoverButton) editCoverButton.style.display = 'block';
            if (editAvatarButton) editAvatarButton.style.display = 'block';

            // Populate edit form with current data
            const fullNameInput = document.getElementById('fullName');
            const bioInput = document.getElementById('bio');
            const locationInput = document.getElementById('location');
            const websiteInput = document.getElementById('website');
            
            if (fullNameInput) fullNameInput.value = data.full_name || '';
            if (bioInput) bioInput.value = data.bio || '';
            if (locationInput) locationInput.value = data.location || '';
            if (websiteInput) websiteInput.value = data.website || '';
        } else {
            // Show follow button for other profiles
            if (editProfileButton) editProfileButton.style.display = 'none';
            if (followButton) {
                followButton.style.display = 'block';
                followButton.textContent = data.is_following ? 'Unfollow' : 'Follow';
            }
            if (editCoverButton) editCoverButton.style.display = 'none';
            if (editAvatarButton) editAvatarButton.style.display = 'none';
        }

        // Once UI is ready, load initial posts
        await loadTabContent('posts');
    } catch (error) {
        console.error('Error loading profile:', error);
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="error-message">
                    <h2>Error Loading Profile</h2>
                    <p>There was a problem loading the profile. Please try again later.</p>
                    <p class="error-details">${escapeHtml(error.message)}</p>
                </div>
            `;
        }
    }
}

function showEditProfileModal() {
    document.getElementById('editProfileModal').style.display = 'flex';
}

function closeEditProfileModal() {
    document.getElementById('editProfileModal').style.display = 'none';
    // Reset file selections
    window.selectedAvatar = null;
    window.selectedCover = null;
}

async function saveProfile() {
    const formData = new FormData();
    
    // Add text fields
    formData.append('full_name', document.getElementById('fullName').value);
    formData.append('bio', document.getElementById('bio').value);
    formData.append('location', document.getElementById('location').value);
    formData.append('website', document.getElementById('website').value);

    // Add files if selected
    if (window.selectedAvatar) {
        formData.append('avatar', window.selectedAvatar);
    }
    if (window.selectedCover) {
        formData.append('cover_photo', window.selectedCover);
    }

    const username = document.body.getAttribute('data-username');
    
    try {
            const response = await fetch(`/api/profiles/me/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.message || 'Profile update failed');
        }

        closeEditProfileModal();
        await loadProfile(username);

    } catch (error) {
        console.error('Error updating profile:', error);
        alert(error.message || 'Failed to update profile. Please try again later.');
    }
}

async function toggleFollow(username) {
    const button = document.querySelector('.follow-button');
    if (!button) {
        console.error('Follow button not found');
        return;
    }

    button.disabled = true;
    const isFollowing = button.textContent.trim() === 'Unfollow';
    
    try {
        const response = await fetch(`/api/profiles/${username}/${isFollowing ? 'unfollow' : 'follow'}/`, {
            method: isFollowing ? 'DELETE' : 'POST',
            credentials: 'include',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (!response.ok) {
            throw new Error(response.statusText);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error('Action failed');
        }

        button.textContent = isFollowing ? 'Follow' : 'Unfollow';
        const followersCount = document.querySelector('.profile-stats .stat:nth-child(2) .stat-number');
        if (followersCount) {
            followersCount.textContent = data.followers_count;
        }

    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Failed to update follow status. Please try again later.');
    } finally {
        button.disabled = false;
    }
}

function switchTab(tab) {
    // Update active tab
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

    // Load content for the selected tab
    loadTabContent(tab);
}

async function loadTabContent(tab) {
    const usernameEl = document.querySelector('.profile-details .username');
    if (!usernameEl) {
        console.error('Username element not found');
        return;
    }

    const container = document.getElementById('profile-posts-container');
    if (!container) return;

    try {
        const username = usernameEl.textContent.substring(1);
        
        // Show loading state
        container.innerHTML = '<div class="loading">Loading content...</div>';
        
        // Fetch data
        const response = await fetch(`/api/profiles/${username}/posts/?tab=${tab}`, {
            credentials: 'include',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update container with content
        if (!data.results || !Array.isArray(data.results)) {
            container.innerHTML = `<div class="error-message">Invalid data format received from server</div>`;
            return;
        }
        
        if (data.results.length === 0) {
            container.innerHTML = `<div class="no-posts">${escapeHtml(`No ${tab} found.`)}</div>`;
            return;
        }
        
        // Clear container and add posts
        container.innerHTML = '';
        data.results.forEach(post => {
            if (window.createPostElement) {
                container.appendChild(window.createPostElement(post));
            } else {
                console.error('createPostElement function not found');
            }
        });
    } catch (error) {
        console.error(`Error loading ${tab}:`, error);
        container.innerHTML = `
            <div class="error-message">
                <h3>Error Loading Content</h3>
                <p>There was a problem loading the ${escapeHtml(tab)}. Please try again later.</p>
                <p class="error-details">${escapeHtml(error.message)}</p>
            </div>
        `;
    }
}
