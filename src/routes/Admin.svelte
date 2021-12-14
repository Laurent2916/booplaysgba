<script lang="ts">
  import { onMount } from 'svelte';

  let websocket: WebSocket | undefined;

  onMount(() => {
    websocket = new WebSocket('ws://localhost:6789/');
  });

  let passwordInput = document.querySelector('#password-text') as HTMLElement;
  let divLogin = document.querySelector('#login') as HTMLElement;
  let divDashboard = document.querySelector('#dashboard') as HTMLElement;
  let stateList = document.querySelector('#stateList') as HTMLElement;
  let saveButton = document.getElementById('save') as HTMLElement;

  saveButton.onclick = function (event) {
    websocket.send(JSON.stringify({ admin: 'save' }));
  };

  function receiveStates(ev) {
    let msg = JSON.parse(ev.data);
    let states = msg.states;
    for (let i = 0; i < states.length; i++) {
      let state = states[i];
      let li = document.createElement('li');
      let button = document.createElement('button');
      button.onclick = () => websocket.send(JSON.stringify({ admin: 'load:' + state }));
      button.appendChild(document.createTextNode(state));
      li.appendChild(button);
      stateList.appendChild(li);
    }
  }

  function authSuccess(ev) {
    let msg = JSON.parse(ev.data);
    if (msg.auth === 'success') {
      divLogin.style.display = 'none';
      divDashboard.style.display = 'unset';
      websocket.removeEventListener('message', authSuccess);
      receiveStates(ev);
    }
  }

  const sendCreds = () => () => {
    if (websocket) {
      let message = JSON.stringify({ auth: (<HTMLInputElement>passwordInput).value });
      websocket.send(message);
      websocket.addEventListener('message', authSuccess);
    }
  };

  passwordInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      sendCreds();
    }
  });
</script>

<title>Télécommande admin</title>

<div id="login">
  <input type="password" id="password-text" />
  <input type="button" id="password-button" value="Login" on:click={sendCreds()} />
</div>

<div id="dashboard">
  <ul id="stateList" />
  <button id="save">save</button>
</div>

<style lang="scss">
  * {
    padding: 0;
    margin: 0;
  }

  #dashboard {
    display: none;
  }
</style>
