const API_URL = 'http://localhost:9080/posts';

async function createPost() {

    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const category = document.getElementById('category').value;

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title,
            description,
            category
        })
    });

    const data = await response.json();

    alert(data.message);

    loadPosts();
}


async function loadPosts() {

    const response = await fetch(API_URL);

    const posts = await response.json();

    const postsDiv = document.getElementById('posts');

    postsDiv.innerHTML = '';

    posts.forEach(post => {

        postsDiv.innerHTML += `
            <div class="post">
                <h2>${post.title}</h2>
                <p>${post.description}</p>
                <p><strong>Category:</strong> ${post.category}</p>
                <p><strong>Created:</strong> ${post.created_date}</p>
                <button onclick="deletePost(${post.id})">Delete</button>
            </div>
        `;
    });
}


async function deletePost(id) {

    await fetch(`${API_URL}/${id}`, {
        method: 'DELETE'
    });

    loadPosts();
}