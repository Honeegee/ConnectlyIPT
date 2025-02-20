document.addEventListener('DOMContentLoaded', function() {
    // Handle profile link click
    document.getElementById('user-profile').addEventListener('click', function(e) {
        e.preventDefault();
        const username = document.body.getAttribute('data-username');
        loadProfile(username);
    });
});

function loadProfile(username) {
    fetch(`/api/profile/${username}`)
        .then(response => response.json())
        .then(data => {
            // Show profile section and hide feed
            document.getElementById('profile-section').style.display = 'block';
            document.getElementById('feed-section').style.display = 'none';

            // Update profile information
            document.getElementById('profile-full-name').textContent = data.full_name || username;
            document.getElementById('profile-username').textContent = '@' + username;
            document.getElementById('profile-bio').textContent = data.bio || '';
            document.getElementById('posts-count').textContent = data.posts_count || 0;
            document.getElementById('followers-count').textContent = data.followers_count || 0;
            document.getElementById('following-count').textContent = data.following_count || 0;

            // Handle edit/follow buttons
            const currentUser = document.body.getAttribute('data-username');
            const editProfileButton = document.getElementById('edit-profile-button');
            const followButton = document.getElementById('follow-button');
            const editCoverButton = document.querySelector('.edit-cover');
            const editAvatarButton = document.querySelector('.edit-avatar');

            if (username === currentUser) {
                editProfileButton.style.display = 'block';
                followButton.style.display = 'none';
                editCoverButton.style.display = 'block';
                editAvatarButton.style.display = 'block';
                
                // Populate edit form with current data
                document.getElementById('fullName').value = data.full_name || '';
                document.getElementById('bio').value = data.bio || '';
                document.getElementById('location').value = data.location || '';
                document.getElementById('website').value = data.website || '';
            } else {
                editProfileButton.style.display = 'none';
                followButton.style.display = 'block';
                editCoverButton.style.display = 'none';
                editAvatarButton.style.display = 'none';
                
                // Set initial follow button state
                followButton.textContent = data.is_following ? 'Unfollow' : 'Follow';
            }

            // Load initial posts
            loadTabContent('posts');
        })
        .catch(error => {
            console.error('Error loading profile:', error);
        });
}

function showEditProfileModal() {
    document.getElementById('editProfileModal').style.display = 'flex';
}

function closeEditProfileModal() {
    document.getElementById('editProfileModal').style.display = 'none';
}

function saveProfile() {
    const data = {
        full_name: document.getElementById('fullName').value,
        bio: document.getElementById('bio').value,
        location: document.getElementById('location').value,
        website: document.getElementById('website').value
    };

    fetch('/api/profile/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            closeEditProfileModal();
            loadProfile(document.body.getAttribute('data-username'));
        }
    })
    .catch(error => {
        console.error('Error updating profile:', error);
    });
}

function toggleFollow(username) {
    const button = document.getElementById('follow-button');
    const isFollowing = button.textContent === 'Unfollow';
    const action = isFollowing ? 'unfollow' : 'follow';

    fetch(`/api/profile/${username}/${action}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.textContent = isFollowing ? 'Follow' : 'Unfollow';
            document.getElementById('followers-count').textContent = data.followers_count;
        }
    })
    .catch(error => {
        console.error('Error toggling follow:', error);
    });
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

function loadTabContent(tab) {
    const username = document.querySelector('#profile-username').textContent.substring(1);
    fetch(`/api/profile/${username}/${tab}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('posts-container');
            container.innerHTML = '';
            
            if (data.results && Array.isArray(data.results)) {
                if (data.results.length === 0) {
                    container.innerHTML = '<div class="no-posts">No posts found.</div>';
                } else {
                    data.results.forEach(post => {
                        // Reuse the createPostElement function from home.js
                        container.appendChild(window.createPostElement(post));
                    });
                }
            }
        })
        .catch(error => {
            console.error(`Error loading ${tab}:`, error);
            const container = document.getElementById('posts-container');
            container.innerHTML = '<div class="error">Error loading content. Please try again.</div>';
        });
}
