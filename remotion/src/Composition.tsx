import { Caption, ImageClip } from "./shared";
import { Documentary } from "./templates/Documentary";
import { Pop } from "./templates/Pop";

export type MainProps = {
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
  audioSrc: string;
  images: ImageClip[];
  captions: Caption[];
  template: string;
  title?: string;
};

// 카테고리별 고정 템플릿 레지스트리. AI는 내용만, 디자인은 여기서 고정.
const TEMPLATES = {
  documentary: Documentary,
  pop: Pop,
} as const;

export const Main = (props: MainProps) => {
  const Template = TEMPLATES[props.template as keyof typeof TEMPLATES] ?? Documentary;
  return (
    <Template
      audioSrc={props.audioSrc}
      images={props.images}
      captions={props.captions}
      title={props.title}
    />
  );
};
