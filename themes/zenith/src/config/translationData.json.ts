/**
 * * Configuration of the i18n system data files and text translations
 * Example translations below are for English and French, with textTranslations used in src/layouts/BlogLayoutCenter.astro and src/components/hero/[hero].astro
 */

/**
 * * Data file configuration for the i18n system
 * Every {Data} key must exist in the below object
 */
import siteDataEn from "./en/siteData.json";
import navDataEn from "./en/navData.json";
import faqDataEn from "./en/faqData.json";
import testimonialDataEn from "./en/testimonialData.json";
import teamDataEn from "./en/teamData.json";
import siteDataFr from "./fr/siteData.json";
import navDataFr from "./fr/navData.json";
import faqDataFr from "./fr/faqData.json";
import testimonialDataFr from "./fr/testimonialData.json";
import teamDataFr from "./fr/teamData.json";

export const dataTranslations = {
  en: {
    siteData: siteDataEn,
    navData: navDataEn,
    faqData: faqDataEn,
    testimonialData: testimonialDataEn,
    teamData: teamDataEn,
  },
  fr: {
    siteData: siteDataFr,
    navData: navDataFr,
    faqData: faqDataFr,
    testimonialData: testimonialDataFr,
    teamData: teamDataFr,
  },
} as const;

/**
 * * Text translations are used with the `useTranslation` function from src/js/i18nUtils.ts to translate various strings on your site.
 *
 * ## Examples
 *
 * ```ts
 * import { getLocaleFromUrl } from "@/js/localeUtils";
 * import { useTranslations } from "@/js/translationUtils";
 * const currLocale = getLocaleFromUrl(Astro.url);
 * const t = useTranslations(currLocale);
 * t("back_to_all_posts"); // this would be "Retour à tous les articles" if the current locale is "fr"
 * ```
 * or
 * ```ts
 * import { useTranslations } from "@/js/translationUtils";
 * const t = useTranslations("fr");
 * t("back_to_all_posts"); // this would be "Retour à tous les articles"
 * ```
 */
export const textTranslations = {
  en: {
    hero_text: "STACK YOUR STOPS. OWN YOUR WEEK.",
    hero_description: "Turn your living to-do list of places into calm, optimized multi-stop trips that fit naturally into your calendar and launch in CarPlay.",

    // blog
    back_to_all_posts: "Back to all posts",
    updated: "Updated",
    share_this_article: "Share this article",
    table_of_contents: "Table of Contents",

    // Authentication - Sign In
    signin_title: "Log in to your account",
    signin_welcome: "Good to have you back!",
    signin_with_google: "Sign in with Google",
    signin_with_apple: "Sign in with Apple",
    signin_with_email: "or sign in with email",
    email_placeholder: "Enter your email",
    password_placeholder: "Enter your password",
    login_button: "Log in",
    no_account: "Don't have an account? ",
    signup_link: "Sign up",

    // Authentication - Sign Up
    signup_title: "Create your account",
    signup_welcome: "Join our community today!",
    signup_with_google: "Sign up with Google",
    signup_with_apple: "Sign up with Apple",
    signup_with_email: "or sign up with email",
    signup_button: "Sign up",
    have_account: "Already have an account? ",
    signin_link: "Sign in",
  },
  fr: {
    hero_text: "STACK YOUR STOPS. OWN YOUR WEEK.",
    hero_description:
      "Je ne parle pas vraiment français donc j'utilise Google Translate pour quelques parties de cette démo.",

    // blog
    back_to_all_posts: "Retour à tous les articles",
    updated: "Mis à jour",
    share_this_article: "Partager cet article",
    table_of_contents: "Table des matières",

    // Authentication - Sign In
    signin_title: "Connectez-vous à votre compte",
    signin_welcome: "Heureux de vous revoir !",
    signin_with_google: "Se connecter avec Google",
    signin_with_apple: "Se connecter avec Apple",
    signin_with_email: "ou connectez-vous avec e-mail",
    email_placeholder: "Entrez votre e-mail",
    password_placeholder: "Entrez votre mot de passe",
    login_button: "Se connecter",
    no_account: "Vous n'avez pas de compte ? ",
    signup_link: "S'inscrire",

    // Authentication - Sign Up
    signup_title: "Créez votre compte",
    signup_welcome: "Rejoignez notre communauté aujourd'hui !",
    signup_with_google: "S'inscrire avec Google",
    signup_with_apple: "S'inscrire avec Apple",
    signup_with_email: "ou inscrivez-vous avec e-mail",
    signup_button: "S'inscrire",
    have_account: "Vous avez déjà un compte ? ",
    signin_link: "Se connecter",
  },
} as const;

/**
 * * Route translations are used to translate route names for the language switcher component
 * This can be useful for SEO reasons. The key does not matter, it just needs to match between languages
 *
 * These routes must be everything after the base domain. So if this is "atlas.com/blog", the route would be "blog"
 * Or if this is "atlas.com/legal/privacy", the route would be "legal/privacy"
 *
 * This also supports wildcards. For example, "categories/*" would match "categories/1" or "categories/2" etc for that language.
 *
 * Note: This works in conjunction with the localizedCollections object below
 */
export const routeTranslations = {
  en: {
    overviewKey: "overview",
    categoryKey: "categories",
    categoryKey2: "categories/*",
    categoryKey3: "categories",
    blogKey: "blog",
    careersKey: "careers",
  },
  fr: {
    overviewKey: "apercu",
    categoryKey: "categories",
    categoryKey2: "categories",
    categoryKey3: "categories/*",
    blogKey: "blog",
    careersKey: "careers",
  },
} as const;

/**
 * * Content collection translations used by the language switcher and hreflang generator
 *
 * Per-collection, per-locale route base mapping (collections to localize are the keys)
 *
 * If you have a key of "blog" then the blog content collection will be localized. This will look
 * for a "mappingKey" in the entry metadata, and use that to map the entry to the correct locale
 *
 * You can use the locale value to map the collection to a different route if desired
 */
export const localizedCollections = {
  blog: {
    en: "blog",
    fr: "blog",
  },
  careers: {
    en: "careers",
    fr: "careers",
  },
  // Add more collections/locales as needed
} as const;
