<template>
  <v-container class="primary fill-height d-flex justify-center align-center">
    <v-card shaped>
      <v-form v-model="validFormFlag">
        <v-toolbar>
          <v-toolbar-title>Login</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
        <v-card-text>
          <v-container pa-10>
            <v-text-field
              prepend-icon="mdi-account"
              label="Username"
              type="text"
              v-model="username"
            ></v-text-field>
            <v-text-field
              prepend-icon="mdi-lock"
              label="Password"
              type="password"
              v-model="password"
              @keyup.enter="loginSubmit"
            ></v-text-field>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="loginSubmit" color="primary" large block>Login</v-btn>
        </v-card-actions>
        <v-container>
          <v-row>
            <v-col>
              <v-btn block plain @click="goToAuthRecoveryPage">Forgot Password?</v-btn>
            </v-col>
            <v-divider vertical></v-divider>
            <v-col>
              <v-btn block plain @click="goToSignupPage">Register</v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-form>
    </v-card>
  </v-container>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';

export default defineComponent({
  name: 'LogIn',
  props: {
    source: String
  },
  setup(props, { root }) {
    const validFormFlag = ref(false);
    const username = ref(null);
    const password = ref(null);

    onMounted(() => {
      const loggedInUser = root.$store.getters.loggedInUser;
      if (!loggedInUser) return;

      if (loggedInUser.role === 'Admin') {
        root.$router.push({ name: 'AdminMain' });
      } else {
        root.$router.push({ name: 'Main' });
      }
    });

    const loginSubmit = () => {
      // Implement login logic here
    };

    const goToSignupPage = () => {

    };

    const goToAuthRecoveryPage = () => {

    };

    return {
      validFormFlag,
      username,
      password,
      loginSubmit,
      goToSignupPage,
      goToAuthRecoveryPage
    };
  }
});
</script>

<style scoped>
</style>
