let currentPage = 1;
let currentFilter = 'all';
let currentPostType = '';
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

document.addEventListener('DOMContentLoaded', () => {
    loadPosts();
    setupFilterListeners();
});

function showCreatePostModal() {
    document.getElementById('createPostModal').style.display = 'block';
    document.getElementById('postContent').focus();
}

function closeCreatePostModal() {
    document.getElementById('createPostModal').style.display = 'none';
    document.getElementById('postTitle').value = '';
    document.getElementById('postContent').value = '';
    document.getElementById('postType').value = 'text';
}

function createPost() {
    const title = document.getElementById('postTitle').value;
    const content = document.getElementById('postContent').value;
    const postType = document.getElementById('postType').value;

    if (!content.trim()) {
        alert('Please write something in your post.');
        return;
    }

    fetch('/api/posts/', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            title: title || undefined,
            content: content,
            post_type: postType
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(post => {
        const container = document.getElementById('posts-container');
        const newPostElement = createPostElement(post);
        container.insertBefore(newPostElement, container.firstChild);
        closeCreatePostModal();
    })
    .catch(error => {
        console.error('Error creating post:', error);
        alert('Error creating post. Please try again.');
    });
}

function setupFilterListeners() {
    // Feed type filters
    document.querySelectorAll('.menu-item[data-filter]').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.menu-item[data-filter]').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            currentFilter = item.dataset.filter;
            currentPage = 1;
            loadPosts();
        });
    });

    // Post type filters
    document.querySelectorAll('.menu-item[data-type]').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.menu-item[data-type]').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            currentPostType = item.dataset.type;
            currentPage = 1;
            loadPosts();
        });
    });

    // Pagination
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadPosts();
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        currentPage++;
        loadPosts();
    });
}

function loadPosts() {
    let url = `/api/feed/?page=${currentPage}`;
    
    if (currentFilter === 'following') {
        url += '&followed=true';
    } else if (currentFilter === 'liked') {
        url += '&liked=true';
    }
    
    if (currentPostType) {
        url += `&post_type=${currentPostType}`;
    }

    fetch(url, {
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const container = document.getElementById('posts-container');
        container.innerHTML = '';

        if (data.results && Array.isArray(data.results)) {
            if (data.results.length === 0) {
                container.innerHTML = '<div class="post"><div class="post-content">No posts found.</div></div>';
            } else {
                data.results.forEach(post => {
                    container.appendChild(createPostElement(post));
                });
            }

            document.getElementById('prev-page').disabled = !data.previous;
            document.getElementById('next-page').disabled = !data.next;
        } else {
            container.innerHTML = '<div class="post"><div class="post-content">Error loading posts.</div></div>';
        }
    })
    .catch(error => {
        console.error('Error loading posts:', error);
        const container = document.getElementById('posts-container');
        container.innerHTML = '<div class="post"><div class="post-content">Error loading posts. Please try again.</div></div>';
        
        if (error.status === 401) {
            window.location.href = '/login/';
        }
    });
}

function createPostElement(post) {
    const postDiv = document.createElement('div');
    postDiv.className = 'post';
    
    const date = new Date(post.created_at).toLocaleDateString();
    
    postDiv.innerHTML = `
        <div class="post-header">
            <div class="avatar"></div>
            <div class="post-info">
                <a href="#" class="post-author">${post.author_username}</a>
                <div class="post-time">${date}</div>
            </div>
        </div>
        <div class="post-content">${post.content}</div>
        <div class="post-stats">
            <div><span id="like-count-${post.id}">${post.like_count}</span> Likes</div>
            <div><span id="comment-count-${post.id}">${post.comment_count}</span> Comments</div>
        </div>
        <div class="post-actions">
            <button class="action-button" onclick="toggleLike(${post.id})">
                Like
            </button>
            <button class="action-button" onclick="toggleComments(${post.id})">
                Comment
            </button>
            <button class="action-button">
                Share
            </button>
        </div>
        <div class="comments-section" id="comments-${post.id}" style="display: none;">
            <div class="comments-list" id="comments-list-${post.id}"></div>
            <div class="comment-form">
                <div class="avatar"></div>
                <input type="text" class="comment-input" placeholder="Write a comment..." 
                       onkeypress="if (event.keyCode === 13) submitComment(${post.id}, this)">
            </div>
        </div>
    `;
    
    return postDiv;
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
    fetch(`/api/posts/${postId}/comments/`, {
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(comments => {
        const commentsList = document.getElementById(`comments-list-${postId}`);
        commentsList.innerHTML = '';
        comments.forEach(comment => {
            commentsList.appendChild(createCommentElement(comment));
        });
    })
    .catch(error => {
        console.error('Error loading comments:', error);
        const commentsList = document.getElementById(`comments-list-${postId}`);
        commentsList.innerHTML = '<div class="comment">Error loading comments.</div>';
    });
}

function createCommentElement(comment) {
    const div = document.createElement('div');
    div.className = 'comment';
    div.innerHTML = `
        <div class="comment-header">
            <span class="comment-author">${comment.author_username}</span>
            <span class="comment-time">${new Date(comment.created_at).toLocaleDateString()}</span>
        </div>
        <div class="comment-content">${comment.text}</div>
    `;
    return div;
}

function submitComment(postId, inputElement) {
    if (event.keyCode !== 13) return;
    
    const content = inputElement.value.trim();
    if (!content) return;

    fetch(`/api/posts/${postId}/comments/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(comment => {
        const commentsList = document.getElementById(`comments-list-${postId}`);
        commentsList.appendChild(createCommentElement(comment));
        const commentCount = document.getElementById(`comment-count-${postId}`);
        commentCount.textContent = parseInt(commentCount.textContent) + 1;
        inputElement.value = '';
    })
    .catch(error => {
        console.error('Error posting comment:', error);
        if (error.response) {
            error.response.json().then(data => {
                console.error('Error details:', data);
                alert(data.error || 'Error posting comment. Please try again.');
            });
        } else {
            alert('Error posting comment. Please try again.');
        }
    });
}

function toggleLike(postId) {
    const button = event.target;
    
    fetch(`/api/posts/${postId}/like/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 201) {
            const likeCount = document.getElementById(`like-count-${postId}`);
            likeCount.textContent = parseInt(likeCount.textContent) + 1;
            button.classList.add('liked');
        } else if (response.status === 400) {
            return fetch(`/api/posts/${postId}/like/`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if (response.ok) {
                    const likeCount = document.getElementById(`like-count-${postId}`);
                    likeCount.textContent = parseInt(likeCount.textContent) - 1;
                    button.classList.remove('liked');
                }
            });
        }
    })
    .catch(error => {
        console.error('Error toggling like:', error);
        if (error.status === 401) {
            window.location.href = '/login/';
        }
    });
}
