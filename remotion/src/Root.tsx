import { Composition } from "remotion";
import { Main, MainProps } from "./Composition";

const defaultProps: MainProps = {
  fps: 30,
  width: 1080,
  height: 1920,
  durationInFrames: 150,
  audioSrc: "voice.mp3",
  images: [],
  captions: [],
};

export const RemotionRoot = () => {
  return (
    <Composition
      id="Main"
      component={Main}
      durationInFrames={150}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={defaultProps}
      calculateMetadata={({ props }) => ({
        durationInFrames: props.durationInFrames,
        fps: props.fps,
        width: props.width,
        height: props.height,
      })}
    />
  );
};
