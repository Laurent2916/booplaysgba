<script lang="ts">
  import { onMount } from 'svelte';

  let websocket: WebSocket | undefined;
  let last_time: number = new Date().getTime();

  onMount(() => {
    websocket = new WebSocket('ws://localhost:6789/');
  });

  const sendAction = (key: string) => () => {
    if (websocket) {
      let current_time: number = new Date().getTime();
      if (current_time - last_time > 500) {
        websocket.send(JSON.stringify({ action: key }));
        last_time = current_time;
      }
    }
  };
</script>

<title>Télécommande</title>

<table class="buttons">
  <tr>
    <td colspan="2" id="l">
      <button on:click={sendAction('l')}>L</button>
    </td>
    <td />
    <td colspan="2" id="r">
      <button on:click={sendAction('r')}>R</button>
    </td>
  </tr>

  <tr>
    <td />
    <td id="up">
      <button on:click={sendAction('up')}> ∧ </button>
    </td>
    <td />
    <td id="select">
      <button on:click={sendAction('select')}> select </button>
    </td>
    <td id="start">
      <button on:click={sendAction('start')}> start </button>
    </td>
  </tr>

  <tr>
    <td id="left">
      <button on:click={sendAction('left')}> &lt; </button>
    </td>
    <td />
    <td id="right">
      <button on:click={sendAction('right')}> > </button>
    </td>
    <td />
    <td />
  </tr>

  <tr>
    <td />
    <td id="down">
      <button on:click={sendAction('down')}> ∨ </button>
    </td>
    <td />
    <td id="a">
      <button on:click={sendAction('a')}>A</button>
    </td>
    <td id="b">
      <button on:click={sendAction('b')}>B</button>
    </td>
  </tr>
</table>

<style lang="scss">
  td {
    text-align: center;
    button {
      width: 10vw;
      height: 10vw;
    }
  }

  #a,
  #b {
    button {
      border-radius: 50%;
    }
  }

  #left,
  #right,
  #up,
  #down {
    button {
      border-radius: 10%;
    }
  }

  #start,
  #select,
  #l,
  #r {
    button {
      width: 20vw;
      border-radius: 25%;
    }
  }

  #r,
  #l {
    padding-bottom: 10vw;
  }
  #r {
    text-align: right;
  }

  #right {
    padding-right: 15vw;
  }
</style>
