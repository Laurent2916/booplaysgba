<script lang="ts">
  import { onMount } from "svelte";

  let websocket: WebSocket | undefined;

  onMount(() => {
    websocket = new WebSocket("ws://localhost:6789/");
  });

  const sendAction = (key: string) => () => {
    if (websocket) websocket.send(JSON.stringify({ action: key }));
  };
</script>

<table class="buttons">
  <tr>
    <td colspan="2" style="padding-bottom: 1rem;">
      <button id="l" on:click={sendAction("l")}>L</button>
    </td>
    <td />
    <td colspan="2" style="padding-bottom: 1rem; text-align: right;">
      <button id="r" on:click={sendAction("r")}>R</button>
    </td>
  </tr>

  <tr>
    <td />
    <td>
      <button id="up" on:click={sendAction("up")}> ∧ </button>
    </td>
    <td />
    <td>
      <button id="select" on:click={sendAction("select")}> select </button>
    </td>
    <td>
      <button id="start" on:click={sendAction("start")}> start </button>
    </td>
  </tr>

  <tr>
    <td>
      <button id="left" on:click={sendAction("left")}> &lt; </button>
    </td>
    <td />
    <td style="padding-right: 20%;">
      <button id="right" on:click={sendAction("right")}> > </button>
    </td>
    <td />
    <td />
  </tr>

  <tr>
    <td />
    <td>
      <button id="down" on:click={sendAction("down")}> ∨ </button>
    </td>
    <td />
    <td>
      <button id="a" on:click={sendAction("a")}>A</button>
    </td>
    <td>
      <button id="b" on:click={sendAction("b")}>B</button>
    </td>
  </tr>
</table>

<style lang="sass">
  td {
    text-align: center;
  }

  button {
    width: 100%;
    height: 100%;
  }

  #a,
  #b {
    border-radius: 50%;
  }

  #left,
  #right,
  #up,
  #down {
    width: 10%;
    height: 10%;
    border-radius: 10%;
  }

  #start,
  #select,
  #l,
  #r {
    width: 20%;
    border-radius: 25%;
  }
</style>
