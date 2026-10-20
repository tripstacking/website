import { type teamMember } from "@/config/types/configDataTypes";

import Image1 from "@images/team/image.png";
import Image2 from "@images/team/image2.png";
import Image3 from "@images/team/image3.png";
import Image4 from "@images/team/image4.png";
import Image5 from "@images/team/image5.png";
import Image6 from "@images/team/image6.png";

export const teamData: teamMember[] = [
  {
    image: Image1,
    name: "Jacob Jones",
    title: "CEO at Zenith",
    bio: `Jacob brings over 15 years of industry experience to his role as CEO. Known for his visionary leadership and strategic thinking, he has guided Zenith through significant growth. Jacob is passionate about fostering innovation and building a positive company culture where every team member can thrive.`,
  },
  {
    image: Image2,
    name: "Cameron Williamson",
    title: "Cybersecurity Analyst",
    bio: `With a background in computer science and network security, Cameron has been instrumental in strengthening Zenith's digital infrastructure. She specializes in threat detection and implementing robust security protocols. Outside of work, Cameron enjoys rock climbing and participating in ethical hacking competitions.`,
  },
  {
    image: Image3,
    name: "Annette Black",
    title: "Full-Stack Developer",
    bio: `Annette is a creative problem-solver who thrives on technical challenges. She has expertise in multiple programming languages and frameworks, allowing her to build seamless user experiences. Annette is dedicated to continuous learning and mentoring junior developers on the team.`,
  },
  {
    image: Image4,
    name: "Esther Howard",
    title: "Designer",
    bio: `Esther brings a unique artistic perspective to every project she touches. With a keen eye for detail and user-centered design principles, she creates intuitive and visually stunning interfaces. Esther is passionate about accessibility and ensuring Zenith's products work for everyone.`,
  },
  {
    image: Image5,
    name: "Brooklyn Simmons",
    title: "Project Estimator",
    bio: `Brooklyn excels at analyzing project requirements and providing accurate timelines and resource allocations. Her background in business analytics and project management helps teams stay on track and within budget. Brooklyn is known for her methodical approach and ability to anticipate potential roadblocks.`,
  },
  {
    image: Image6,
    name: "Jerome Bell",
    title: "Salesman",
    bio: `Jerome has a natural talent for building relationships and understanding client needs. His consultative approach to sales has helped expand Zenith's client base significantly. Jerome is dedicated to ensuring customers find the right solutions for their unique challenges and remains a trusted advisor long after the initial sale.`,
  },
];

export default teamData;
