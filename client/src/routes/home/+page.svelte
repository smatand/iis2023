<script>
    let message = '';

    async function fetchData() {
        const response = await fetch(('http://localhost:5000/api/home'));
        const data = await response.json();
        message = data.message;
    }

    fetchData();
</script>

<h1>{message}</h1>