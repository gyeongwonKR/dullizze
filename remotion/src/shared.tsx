import {
  AbsoluteFill,
  Img,
  Sequence,
  staticFile,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type ImageClip = {
  src: string;
  startInFrames: number;
  durationInFrames: number;
};

export type Caption = {
  text: string;
  startMs: number;
  endMs: number;
};

export type TemplateProps = {
  audioSrc: string;
  images: ImageClip[];
  captions: Caption[];
  title?: string;
};

// 한 이미지의 Ken Burns 줌(시퀀스 내부 프레임 기준).
export const KenBurnsImage = ({
  src,
  durationInFrames,
  to = 1.12,
}: {
  src: string;
  durationInFrames: number;
  to?: number;
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [1, to], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
        }}
      />
    </AbsoluteFill>
  );
};

// 배경 이미지들을 순서대로(각자 Ken Burns) 깔아줌.
export const BackgroundImages = ({
  images,
  to = 1.12,
}: {
  images: ImageClip[];
  to?: number;
}) => (
  <>
    {images.map((img, i) => (
      <Sequence key={i} from={img.startInFrames} durationInFrames={img.durationInFrames}>
        <KenBurnsImage src={img.src} durationInFrames={img.durationInFrames} to={to} />
      </Sequence>
    ))}
  </>
);

// 현재 프레임 시각에 해당하는 자막 텍스트(없으면 null).
export const useCurrentCaption = (captions: Caption[]): string | null => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const c = captions.find((x) => ms >= x.startMs && ms < x.endMs);
  return c ? c.text : null;
};
