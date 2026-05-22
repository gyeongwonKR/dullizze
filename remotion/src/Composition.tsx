import { Bgm, Caption, ImageClip } from "./shared";
import { Banner } from "./templates/Banner";
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
  bgm?: Bgm;
  // banner 템플릿 전용.
  headlineMain?: string;
  headlineAccent?: string;
  channelName?: string;
  footerMain?: string;
  footerAccent?: string;
  accentColor?: string;
};

// 카테고리별 고정 템플릿 레지스트리. AI는 내용만, 디자인은 여기서 고정.
const TEMPLATES = {
  documentary: Documentary,
  pop: Pop,
  banner: Banner,
} as const;

export const Main = (props: MainProps) => {
  const Template = TEMPLATES[props.template as keyof typeof TEMPLATES] ?? Documentary;
  return (
    <Template
      audioSrc={props.audioSrc}
      images={props.images}
      captions={props.captions}
      title={props.title}
      bgm={props.bgm}
      headlineMain={props.headlineMain}
      headlineAccent={props.headlineAccent}
      channelName={props.channelName}
      footerMain={props.footerMain}
      footerAccent={props.footerAccent}
      accentColor={props.accentColor}
    />
  );
};
