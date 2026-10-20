import { type TestimonialItem } from "../types/configDataTypes";
import BowTiedFocus from "@images/BowTiedFocus.jpg";
import TravisB from "@images/travis-b.png";
import Isaac from "@images/isaac_saas.jpg";
import Aniket from "@images/aniket_p.jpg";
import David from "@images/david-g-davedev.png";
import Damiano from "@images/damiano.jpg";

export const testimonialData: TestimonialItem[] = [
  {
    avatar: BowTiedFocus,
    name: "Elena R.",
    title: "Working Parent & Commuter",
    testimonial: `Trip Stacking turned my chaotic Saturday of 7 scattered errands into two calm 45-minute loops on Tuesday and Thursday—and put a single clean block on my calendar.`,
  },
  {
    avatar: TravisB,
    name: "Marcus T.",
    title: "Daily CarPlay Driver",
    testimonial: `The 'groceries last' and 'minimize unprotected left turns' rules are magic. I tap the calendar event on my CarPlay screen and every stop is already in the exact right order.`,
  },
  {
    avatar: Isaac,
    name: "Priya K.",
    title: "Product Operations Lead",
    testimonial: `Other apps either do simple to-do lists or single A-to-B routing. Trip Stacking actually knows store hours, how long I spend at the post office, and when traffic is quiet.`,
  },
  {
    avatar: Aniket,
    name: "David G.",
    title: "Small Business Owner",
    testimonial: `Having 'visit the bank before the hardware store' automatically respected across my week saves me at least two hours of backtracking every single week.`,
  },
  {
    avatar: David,
    name: "Hannah M.",
    title: "Freelance Designer",
    testimonial: `I love that it doesn't clutter my calendar with six tiny 15-minute reminders. One Stacked Trip block with total drive + dwell time is how my brain actually works.`,
  },
  {
    avatar: Damiano,
    name: "Samir V.",
    title: "iOS & Apple Maps User",
    testimonial: `Zero friction from start to finish. It splits overflow errands onto my Friday afternoon window automatically and exports straight to Apple Maps and CarPlay.`,
  },
];

export default testimonialData;
