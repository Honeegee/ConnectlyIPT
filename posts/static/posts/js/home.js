// Global variables with proper initialization
const state = {
    currentPage: 1,
    currentFilter: 'all',
    currentPostType: '',
    csrfToken: null,
    isLoading: false,
    debounceTimers: {} // For debouncing actions
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Get CSRF token safely
        const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfElement) {
            throw new Error('CSRF token not found');
        }
        state.csrfToken = csrfElement.value;

        // Only initialize posts functionality if we're on the home page
        const postsContainer = document.getElementById('posts-container');
        if (postsContainer) {
            // Initialize modals
            initializeModals();
            
            // Initialize app
            loadPosts();
            setupFilterListeners();
            setupMediaListeners();
        }
    } catch (error) {
        console.error('Error initializing app:', error);
        alert('Error initializing application. Please refresh the page.');
    }
});

// Debounce helper function
function debounce(fn, delay, id) {
    return (...args) => {
        if (state.debounceTimers[id]) {
            clearTimeout(state.debounceTimers[id]);
        }
        state.debounceTimers[id] = setTimeout(() => {
            fn.apply(null, args);
            delete state.debounceTimers[id];
        }, delay);
    };
}

// Reusable API response handler
function handleAPIResponse(response) {
    return response.json().then(data => {
        if (!response.ok) {
            const errorMsg = data.error || 
                (data.detail ? data.detail : 
                Object.values(data)[0] || 'API request failed');
            throw new Error(errorMsg);
        }
        return data;
    });
}

function initializeModals() {
    const modals = ['createPostModal', 'editPostModal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    });
}

function showCreatePostModal() {
    const modal = document.getElementById('createPostModal');
    const content = document.getElementById('postContent');
    if (!modal || !content) return;

    modal.style.display = 'flex';
    content.focus();
}

function closeCreatePostModal() {
    const modal = document.getElementById('createPostModal');
    const title = document.getElementById('postTitle');
    const content = document.getElementById('postContent');
    const type = document.getElementById('postType');
    const mediaInputs = document.getElementById('mediaInputs');
    const mediaPreview = document.getElementById('mediaPreview');
    const imageInput = document.getElementById('imageInput');
    const videoInput = document.getElementById('videoInput');

    if (!modal) return;
    
    modal.style.display = 'none';
    if (title) title.value = '';
    if (content) content.value = '';
    if (type) type.value = 'text';
    
    // Reset media inputs if they exist
    if (mediaInputs) mediaInputs.style.display = 'none';
    if (mediaPreview) mediaPreview.style.display = 'none';
    if (imageInput) imageInput.value = '';
    if (videoInput) videoInput.value = '';
}

function showEditPostModal(postId, content, title, postType) {
    const modal = document.getElementById('editPostModal');
    const editId = document.getElementById('editPostId');
    const editTitle = document.getElementById('editPostTitle');
    const editContent = document.getElementById('editPostContent');
    const editType = document.getElementById('editPostType');

    if (!modal || !editId || !editTitle || !editContent || !editType) return;

    modal.style.display = 'flex';
    editId.value = postId;
    editTitle.value = title;
    editContent.value = content;
    editType.value = postType;
}

function closeEditPostModal() {
    const modal = document.getElementById('editPostModal');
    if (!modal) return;
    modal.style.display = 'none';
}

function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }

    fetch(`api/posts/${postId}/`, {
        method: 'DELETE',
            credentials: 'same-origin',
        headers: {
            'X-CSRFToken': state.csrfToken
        }
    })
    .then(handleAPIResponse)
    .then(() => {
        const postElement = document.querySelector(`.post[data-post-id="${postId}"]`);
        if (postElement) {
            postElement.remove();
        }
    })
    .catch(error => {
        console.error('Error deleting post:', error);
        alert(error.message || 'Error deleting post. Please try again.');
    });
}

function isUserAdmin() {
    return document.body.dataset.isAdmin === 'true';
}

function editPost(postId) {
    try {
        if (!isUserAdmin() && !document.querySelector(`.post[data-post-id="${postId}"]`).classList.contains('user-post')) {
            alert('You do not have permission to edit this post.');
            return;
        }

        const title = document.getElementById('editPostTitle').value;
        const content = document.getElementById('editPostContent').value;
        const postType = document.getElementById('editPostType').value;

        if (!content.trim()) {
            alert('Please write something in your post.');
            return;
        }

    fetch(`api/posts/${postId}/`, {
        method: 'PUT',
        credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': state.csrfToken
            },
            body: JSON.stringify({
                title: title || '',
                content: content,
                post_type: postType
            })
        })
        .then(handleAPIResponse)
        .then(updatedPost => {
            const postElement = document.querySelector(`.post[data-post-id="${postId}"]`);
            if (postElement) {
                const newPostElement = createPostElement(updatedPost);
                postElement.replaceWith(newPostElement);
            }
            closeEditPostModal();
        })
        .catch(error => {
            console.error('Error updating post:', error);
            alert(error.message || 'Error updating post. Please try again.');
        });
    } catch (error) {
        console.error('Error updating post:', error);
        alert(error.message || 'Error updating post. Please try again.');
    }
}

function setupMediaListeners() {
    const imageInput = document.getElementById('imageInput');
    const videoInput = document.getElementById('videoInput');
    
    // Only set up listeners if we're on the home page
    if (!imageInput || !videoInput) return;
    
    imageInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            if (!validateMediaFile(file, 'image')) {
                e.target.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                const imagePreview = document.getElementById('imagePreview');
                const mediaPreview = document.getElementById('mediaPreview');
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                mediaPreview.style.display = 'block';
            };
            reader.onerror = () => {
                console.error('Error reading file');
                alert('Error previewing file. Please try again.');
                e.target.value = '';
            };
            reader.readAsDataURL(file);
        }
    });

    videoInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            if (!validateMediaFile(file, 'video')) {
                e.target.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                const videoPreview = document.getElementById('videoPreview');
                const mediaPreview = document.getElementById('mediaPreview');
                videoPreview.src = e.target.result;
                videoPreview.style.display = 'block';
                mediaPreview.style.display = 'block';
            };
            reader.onerror = () => {
                console.error('Error reading file');
                alert('Error previewing file. Please try again.');
                e.target.value = '';
            };
            reader.readAsDataURL(file);
        }
    });
}

function validateMediaFile(file, type) {
    const maxSize = 50 * 1024 * 1024; // 50MB
    const allowedImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    const allowedVideoTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'];

    if (file.size > maxSize) {
        alert('File size must be less than 50MB');
        return false;
    }

    if (type === 'image' && !allowedImageTypes.includes(file.type)) {
        alert('Please upload a valid image file (JPEG, PNG, GIF, or WebP)');
        return false;
    }

    if (type === 'video' && !allowedVideoTypes.includes(file.type)) {
        alert('Please upload a valid video file (MP4, MOV, AVI, or WebM)');
        return false;
    }

    return true;
}

function createPost() {
    if (state.isLoading) return;
    state.isLoading = true;

    const title = document.getElementById('postTitle').value;
    const content = document.getElementById('postContent').value;
    const postType = document.getElementById('postType').value;
    const imageInput = document.getElementById('imageInput');
    const videoInput = document.getElementById('videoInput');

    if (!content.trim() && postType === 'text') {
        alert('Please write something in your post.');
        state.isLoading = false;
        return;
    }

    if (postType === 'image' && !imageInput.files[0]) {
        alert('Please select an image for your post.');
        state.isLoading = false;
        return;
    }

    if (postType === 'video' && !videoInput.files[0]) {
        alert('Please select a video for your post.');
        state.isLoading = false;
        return;
    }

    try {
        // For media posts (image/video)
        if (postType !== 'text') {
            const formData = new FormData();
            formData.append('title', title || '');
            formData.append('content', content);
            formData.append('post_type', postType);
            
            const mediaFile = postType === 'image' ? imageInput.files[0] : videoInput.files[0];
            
            const metadata = {
                post_type: postType,
                timestamp: new Date().toISOString(),
                file_info: {
                    name: mediaFile.name,
                    type: mediaFile.type,
                    size: mediaFile.size
                }
            };
            
            formData.append('metadata', JSON.stringify(metadata));
            formData.append('media', mediaFile);

            fetch('api/posts/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': state.csrfToken
                },
                body: formData
            })
            .then(handleAPIResponse)
            .then(handleSuccess)
            .catch(handleError)
            .finally(() => {
                state.isLoading = false;
            });
        } else {
            fetch('/api/posts/', {
                method: 'POST',
            credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': state.csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title || '',
                    content: content,
                    post_type: postType,
                    metadata: {
                        post_type: postType,
                        timestamp: new Date().toISOString()
                    }
                })
            })
            .then(handleAPIResponse)
            .then(handleSuccess)
            .catch(handleError)
            .finally(() => {
                state.isLoading = false;
            });
        }
    } catch (error) {
        handleError(error);
        state.isLoading = false;
    }
}

function handleSuccess(post) {
    const container = document.getElementById('posts-container');
    if (container) {
        const newPostElement = createPostElement(post);
        container.insertBefore(newPostElement, container.firstChild);
        closeCreatePostModal();
    }
}

function handleError(error) {
    console.error('Error:', error);
    alert(error.message || 'An error occurred. Please try again.');
}

function toggleMediaInput() {
    const mediaInputs = document.getElementById('mediaInputs');
    const imageInput = document.getElementById('imageInput');
    const videoInput = document.getElementById('videoInput');
    const imagePreview = document.getElementById('imagePreview');
    const videoPreview = document.getElementById('videoPreview');
    const mediaPreview = document.getElementById('mediaPreview');
    const postType = document.getElementById('postType');

    // Return if any required element is missing
    if (!mediaInputs || !imageInput || !videoInput || !imagePreview || 
        !videoPreview || !mediaPreview || !postType) {
        return;
    }

    // Reset all media elements
    imageInput.style.display = 'none';
    videoInput.style.display = 'none';
    imagePreview.style.display = 'none';
    videoPreview.style.display = 'none';
    mediaPreview.style.display = 'none';
    
    if (postType.value === 'image') {
        mediaInputs.style.display = 'block';
        imageInput.style.display = 'block';
        imageInput.click();
    } else if (postType.value === 'video') {
        mediaInputs.style.display = 'block';
        videoInput.style.display = 'block';
        videoInput.click();
    } else {
        mediaInputs.style.display = 'none';
    }
}

function setupFilterListeners() {
    // Only set up listeners if we're on the home page
    const container = document.getElementById('posts-container');
    if (!container) return;

    const prevPage = document.getElementById('prev-page');
    const nextPage = document.getElementById('next-page');

    document.querySelectorAll('.menu-item[data-filter]').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.menu-item[data-filter]').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            state.currentFilter = item.dataset.filter;
            state.currentPage = 1;
            loadPosts();
        });
    });

    document.querySelectorAll('.menu-item[data-type]').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.menu-item[data-type]').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            state.currentPostType = item.dataset.type;
            state.currentPage = 1;
            loadPosts();
        });
    });

    if (prevPage) {
        prevPage.addEventListener('click', () => {
            if (state.currentPage > 1) {
                state.currentPage--;
                loadPosts();
            }
        });
    }

    if (nextPage) {
        nextPage.addEventListener('click', () => {
            state.currentPage++;
            loadPosts();
        });
    }
}

// Create DOM elements for posts
function createPostElement(post) {
    const postItem = document.createElement('li');
    postItem.className = `post${post.author_username === document.body.dataset.username ? ' user-post' : ''}`;
    postItem.setAttribute('data-post-id', post.id);
    
    const date = new Date(post.created_at).toLocaleDateString();
    const isOwnPost = post.author_username === document.body.dataset.username;
    
    postItem.innerHTML = `
        <div class="post-header">
            <div class="avatar"></div>
            <div class="post-info">
                <a href="/profile/${post.author_username}/" class="post-author">${post.author_username}</a>
                <div class="post-time">${date}</div>
            </div>
            ${!isOwnPost ? `
                <button class="follow-button${post.is_following ? ' following' : ''}" onclick="toggleFollow('${post.author_username}', this)">
                    ${post.is_following ? 'Following' : 'Follow'}
                </button>
            ` : ''}
        </div>
        <div class="post-content">
            ${post.content ? post.content.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;') : ''}
            ${post.post_type === 'image' ? 
                `<img src="${post.media_url}" alt="Post image" style="max-width: 100%; margin-top: 10px;">` : 
                post.post_type === 'video' ? 
                `<video src="${post.media_url}" controls style="max-width: 100%; margin-top: 10px;"></video>` : 
                ''}
        </div>
        <div class="post-stats">
            <div class="likes-stat" onclick="toggleLikes(${post.id})">
                <span id="like-count-${post.id}">${post.like_count || 0}</span> Likes
            </div>
            <div class="comments-stat" onclick="toggleComments(${post.id})">
                <span id="comment-count-${post.id}">${post.comment_count || 0}</span> Comments
            </div>
        </div>
        <div class="post-actions">
            <button class="action-button${post.has_liked ? ' liked' : ''}" onclick="toggleLike(${post.id}, event)">
                Like
            </button>
            <button class="action-button" onclick="toggleComments(${post.id})">
                Comment
            </button>
            ${post.can_edit ? `
                <button class="action-button" onclick='showEditPostModal(${post.id}, "${post.content.replace(/"/g, '&quot;')}", "${(post.title || '').replace(/"/g, '&quot;')}", "${post.post_type}")'>
                    Edit
                </button>
                <button class="action-button" onclick="deletePost(${post.id})">
                    Delete
                </button>
            ` : ''}
        </div>
        <div class="likes-section" id="likes-${post.id}" style="display: none;">
            <div class="likes-list" id="likes-list-${post.id}"></div>
        </div>
        <div class="comments-section" id="comments-${post.id}" style="display: none;">
            <div class="comments-list" id="comments-list-${post.id}"></div>
            <div class="comment-form">
                <div class="avatar"></div>
                <input type="text" class="comment-input" placeholder="Write a comment..." 
                       onkeyup="handleCommentInput(event, ${post.id}, this)">
            </div>
        </div>
    `;
    
    fetch(`api/posts/${post.id}/like/`, {
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            'X-CSRFToken': state.csrfToken
        }
    })
    .then(handleAPIResponse)
    .then(likes => {
        const likesList = document.getElementById(`likes-list-${post.id}`);
        if (likesList) {
            likesList.innerHTML = '';
            if (likes.length === 0) {
                likesList.innerHTML = '<div class="like-item">No likes yet</div>';
                return;
            }
            likes.forEach(like => {
                const likeElement = document.createElement('div');
                likeElement.className = 'like-item';
                likeElement.innerHTML = `
                    <div class="like-user">
                        <div class="avatar"></div>
                        <a href="/profile/${like.user_username}/" class="like-username">${like.user_username}</a>
                    </div>
                `;
                likesList.appendChild(likeElement);
            });
        }
    })
    .catch(error => {
        console.error('Error loading likes:', error);
        const likesList = document.getElementById(`likes-list-${post.id}`);
        if (likesList) {
            likesList.innerHTML = '<div class="like-item">Error loading likes.</div>';
        }
    });
    
    return postItem;
}

function loadPosts() {
    if (state.isLoading) return;
    state.isLoading = true;

    const container = document.getElementById('posts-container');
    if (!container) {
        console.error('Posts container not found');
        state.isLoading = false;
        return;
    }
    
    container.innerHTML = '<li class="loading">Loading posts...</li>';

    let url = `api/feed/?page=${state.currentPage}&_=${Date.now()}`;
    
    if (state.currentFilter === 'following') {
        url += '&followed=true';
    } else if (state.currentFilter === 'liked') {
        url += '&liked=true';
    }
    
    if (state.currentPostType) {
        url += `&post_type=${state.currentPostType}`;
    }

    fetch(url, {
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': state.csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(handleAPIResponse)
    .then(data => {
        container.innerHTML = '';

        if (data.results && Array.isArray(data.results)) {
            if (data.results.length === 0) {
                container.innerHTML = '<li class="post"><div class="post-content">No posts found.</div></li>';
            } else {
                data.results.forEach(post => {
                    container.appendChild(createPostElement(post));
                });
            }

            const prevPage = document.getElementById('prev-page');
            const nextPage = document.getElementById('next-page');
            
            if (prevPage) prevPage.disabled = !data.previous;
            if (nextPage) nextPage.disabled = !data.next;
        } else {
            throw new Error('Invalid response format');
        }
    })
    .catch(error => {
        console.error('Error loading posts:', error);
        container.innerHTML = '<li class="post"><div class="post-content">Error loading posts. Please try again.</div></li>';
        
        if (error.status === 401) {
            window.location.href = '/login/';
        }
    })
    .finally(() => {
        state.isLoading = false;
    });
}

// Make functions available globally for profile.js
window.createPostElement = createPostElement;

async function toggleFollow(username, button) {
    if (state.isLoading) return;
    state.isLoading = true;

    const isFollowing = button.classList.contains('following');
    
    try {
        const response = await fetch(`api/profiles/${username}/follow/`, {
            method: isFollowing ? 'DELETE' : 'POST',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': state.csrfToken
            }
        });

        const data = await handleAPIResponse(response);

        if (response.ok) {
            button.classList.toggle('following');
            button.textContent = isFollowing ? 'Follow' : 'Following';
        }
    } catch (error) {
        console.error('Error toggling follow:', error);
        alert(error.message || 'Error toggling follow. Please try again.');
    } finally {
        state.isLoading = false;
    }
}


function toggleComments(postId) {
    const commentsSection = document.getElementById(`comments-${postId}`);
    if (commentsSection.style.display === 'none') {
        commentsSection.style.display = 'block';
        loadComments(postId);
    } else {
        commentsSection.style.display = 'none';
    }
}

function loadComments(postId) {
    const commentsList = document.getElementById(`comments-list-${postId}`);
    commentsList.innerHTML = '<div class="loading">Loading comments...</div>';

    fetch(`api/posts/${postId}/comments/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': state.csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                console.error('Response:', text);
                throw new Error(`HTTP error! status: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(comments => {
        commentsList.innerHTML = '';
        comments.forEach(comment => {
            commentsList.appendChild(createCommentElement(comment));
        });
    })
    .catch(error => {
        console.error('Error loading comments:', error);
        commentsList.innerHTML = '<div class="comment">Error loading comments. Please try refreshing the page.</div>';
    });
}

function createCommentElement(comment) {
    const div = document.createElement('div');
    div.className = 'comment';
    div.innerHTML = `
        <div class="comment-header">
            <a href="/profile/${comment.author_username}/" class="comment-author">${comment.author_username}</a>
            <span class="comment-time">${new Date(comment.created_at).toLocaleDateString()}</span>
        </div>
        <div class="comment-content">${comment.text}</div>
    `;
    return div;
}

function submitComment(postId, inputElement) {
    const content = inputElement.value.trim();
    if (!content) return;

    if (state.isLoading) return;
    state.isLoading = true;

    inputElement.disabled = true;

    fetch(`api/posts/${postId}/comments/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': state.csrfToken
        },
        body: JSON.stringify({ 
            text: content,
            post: postId
        })
    })
    .then(handleAPIResponse)
    .then(comment => {
        const commentsList = document.getElementById(`comments-list-${postId}`);
        commentsList.appendChild(createCommentElement(comment));
        const commentCount = document.getElementById(`comment-count-${postId}`);
        commentCount.textContent = parseInt(commentCount.textContent) + 1;
        inputElement.value = '';
    })
    .catch(error => {
        console.error('Error posting comment:', error);
        alert(error.message || 'Error posting comment. Please try again.');
    })
    .finally(() => {
        inputElement.disabled = false;
        state.isLoading = false;
    });
}

function fetchLikes(postId) {
    fetch(`api/posts/${postId}/like/`, {
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': state.csrfToken
        }
    })
    .then(handleAPIResponse)
    .then(likes => {
        const likesList = document.getElementById(`likes-list-${postId}`);
        if (likesList) {
            likesList.innerHTML = '';
            if (likes.length === 0) {
                likesList.innerHTML = '<div class="like-item">No likes yet</div>';
                return;
            }
            likes.forEach(like => {
                const likeElement = document.createElement('div');
                likeElement.className = 'like-item';
                likeElement.innerHTML = `
                    <div class="like-user">
                        <div class="avatar"></div>
                        <a href="profile/${like.user_username}/" class="like-username">${like.user_username}</a>
                    </div>
                `;
                likesList.appendChild(likeElement);
            });
        }
    })
    .catch(error => {
        console.error('Error loading likes:', error);
        const likesList = document.getElementById(`likes-list-${postId}`);
        if (likesList) {
            likesList.innerHTML = '<div class="like-item">Error loading likes.</div>';
        }
    });
}

function toggleLikes(postId) {
    const likesSection = document.getElementById(`likes-${postId}`);
    if (likesSection.style.display === 'none') {
        likesSection.style.display = 'block';
        fetchLikes(postId);
    } else {
        likesSection.style.display = 'none';
    }
}

function handleCommentInput(event, postId, inputElement) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        submitComment(postId, inputElement);
    }
}

async function toggleLike(postId, event) {
    if (state.isLoading) return;
    state.isLoading = true;

    const button = event.currentTarget;
    button.disabled = true;
    const likeCount = document.getElementById(`like-count-${postId}`);

    try {
        // First try to create a like
        const createResponse = await fetch(`/api/posts/${postId}/like/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': state.csrfToken
            },
            body: JSON.stringify({
                post: postId
            })
        });

        // If 201, like was created
        if (createResponse.status === 201) {
            likeCount.textContent = parseInt(likeCount.textContent) + 1;
            button.classList.add('liked');
        } 
        // If 400, post is already liked - try to unlike
        else if (createResponse.status === 400) {
            const deleteResponse = await fetch(`/api/posts/${postId}/like/`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                'Accept': 'application/json',
                'X-CSRFToken': state.csrfToken
                }
            });

            if (deleteResponse.ok) {
                likeCount.textContent = parseInt(likeCount.textContent) - 1;
                button.classList.remove('liked');
            } else {
                throw new Error('Failed to unlike post');
            }
        } 
        // Any other status is an error
        else {
            throw new Error('Failed to toggle like');
        }
    } catch (error) {
        console.error('Error toggling like:', error);
        alert(error.message || 'Error toggling like. Please try again.');
        
        if (error.status === 401) {
            window.location.href = 'login/';
        }
    } finally {
        button.disabled = false;
        state.isLoading = false;
    }
}
