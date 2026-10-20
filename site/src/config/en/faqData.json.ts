import { type FaqItem } from "../types/configDataTypes";

export const faqData: FaqItem[] = [
  {
    question: "How is Trip Stacking different from a normal to-do app or Maps app?",
    answer: `Traditional to-do lists know what you need to do, and navigation apps know how to get from point A to point B—but neither orchestrates when and in what order to combine stops across your week. Trip Stacking solves store hours, dwell durations, traffic corridors, and calendar blocks simultaneously.`,
  },
  {
    question: "How does Trip Stacking keep my calendar clean?",
    answer: `Instead of cluttering your calendar with 6 separate micro-events for every errand, Trip Stacking creates one consolidated calendar block per stacked trip—combining drive time and per-stop dwell durations with a one-tap link to launch turn-by-turn directions.`,
  },
  {
    question: "Can I enforce ordering rules like 'visit the bank before the hardware store' or 'groceries last'?",
    answer: `Yes! Every place on your to-do list supports relative priority and precedence constraints—so frozen groceries are always scheduled as your final stop before heading home, and prerequisite errands always happen first.`,
  },
  {
    question: "What does low-stress routing mean?",
    answer: `The fastest route on paper isn't always the best drive if it forces unprotected left turns across four lanes of rush-hour traffic. Trip Stacking penalizes high-stress maneuvers and learns your preferred local corridors over time.`,
  },
  {
    question: "How do I view my route and use it with Apple CarPlay?",
    answer: `You don't need to export stops to external map apps. Trip Stacking displays your complete multi-stop route directly inside the app and connects natively with Apple CarPlay so you can follow every stop and dwell window right from your dashboard.`,
  },
  {
    question: "What happens if all my errands don't fit into one afternoon?",
    answer: `Trip Stacking's multi-day optimizer automatically splits overflow or conflicting stops onto your next best calendar window while respecting deadlines and store opening hours.`,
  },
];

export default faqData;
