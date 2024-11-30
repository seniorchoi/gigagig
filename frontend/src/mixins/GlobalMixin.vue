<script>
export default {
    methods: {
        goToLoginPage() {
            this.$router.push({ name: 'LoginPage' });
        },
        doLogout() {
            AuthenticationApi.doLogout().then(() => {
                this.$store.commit('doLogout');
                this.$router.push({ name: 'LoginPage' });
            });
        }
    }
};
</script>
