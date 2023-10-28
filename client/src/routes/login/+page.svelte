<script>
  import { useForm, validators, HintGroup, Hint, required } from "svelte-use-form";
  import { goto } from '$app/navigation';

  const form = useForm();
  let errorMessage = "";

  async function handleLogin() {
    const { username, password } = $form.values;
    const payload = { username, password };

    console.log('Logging in with payload:', payload);

    try {
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.login === true) {
        if (data.role == 'user') {
            goto('/home');
        }
      } else {
        errorMessage = data.message;
      }
    } catch (error) {
      console.error('An error occurred during login:', error);
    }
  }
</script>

<p class="error-message">{errorMessage}</p>

<form use:form on:submit|preventDefault={handleLogin}>
  <h1>Login</h1>

  <input type="username" name="username" use:validators={[required]} />
  <HintGroup for="username">
    <Hint on="required">This is a mandatory field</Hint>
  </HintGroup>

  <input type="password" name="password" use:validators={[required]} />
  <Hint for="password" on="required">This is a mandatory field</Hint>

  <button disabled={!$form.valid}>Login</button>
</form>

<style>
	:global(.touched:invalid) {
		border-color: red;
		outline-color: red;
	}
  .error-message {
    color: red;
    font-weight: bold;
  }
</style>